import io
from django.http import FileResponse
from django.conf import settings
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from .models import Paper
from .serializers import PaperListSerializer, PaperDetailSerializer, PaperGenerateSerializer
from .gemini_service import generate_paper
from apps.subscriptions.models import CreditWallet


class PaperGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PaperGenerateSerializer,
        summary='Generate a new exam paper using Gemini AI',
        tags=['Papers'],
    )
    def post(self, request):
        serializer = PaperGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Check credits
        try:
            wallet = CreditWallet.objects.get(user=request.user)
            if wallet.credits < 1:
                return Response({'error': 'Insufficient credits. Please upgrade your plan.'}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except CreditWallet.DoesNotExist:
            return Response({'error': 'Credit wallet not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create paper record
        paper = Paper.objects.create(
            teacher=request.user,
            board=data['board'],
            class_name=data['class_name'],
            subject=data['subject'],
            difficulty=data['difficulty'],
            topics=data.get('topics', ''),
            adhere_marking_scheme=data['adhere_marking_scheme'],
            status=Paper.STATUS_GENERATING,
        )

        try:
            result = generate_paper(
                board=data['board'],
                class_name=data['class_name'],
                subject=data['subject'],
                difficulty=data['difficulty'],
                topics=data.get('topics', ''),
                adhere_marking_scheme=data['adhere_marking_scheme'],
                preferred_language=request.user.preferred_language or 'en'
            )

            paper.title = result.get('title', f"{data['board']} {data['class_name']} {data['subject']} Paper")
            paper.paper_content = result
            paper.answer_key = {s['name']: s['questions'] for s in result.get('sections', [])}
            paper.paper_text = result.get('paper_text', '')
            paper.answer_key_text = result.get('answer_key_text', '')
            paper.status = Paper.STATUS_READY
            paper.credits_used = 1
            paper.save()

            # Deduct credit
            wallet.credits -= 1
            wallet.save()

            return Response(PaperDetailSerializer(paper).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            paper.status = Paper.STATUS_FAILED
            paper.save()
            return Response({'error': f'Paper generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaperListView(generics.ListAPIView):
    serializer_class = PaperListSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List all my generated papers', tags=['Papers'])
    def get_queryset(self):
        return Paper.objects.filter(teacher=self.request.user)


class PaperDetailView(generics.RetrieveAPIView):
    serializer_class = PaperDetailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Get paper detail with content and answer key', tags=['Papers'])
    def get_queryset(self):
        return Paper.objects.filter(teacher=self.request.user)


class PaperDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Download paper as PDF', tags=['Papers'])
    def get(self, request, pk):
        try:
            paper = Paper.objects.get(pk=pk, teacher=request.user)
        except Paper.DoesNotExist:
            return Response({'error': 'Paper not found'}, status=status.HTTP_404_NOT_FOUND)

        if paper.status != Paper.STATUS_READY:
            return Response({'error': 'Paper is not ready yet'}, status=status.HTTP_400_BAD_REQUEST)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin_left = 2 * cm
        margin_right = width - 2 * cm
        usable_width = margin_right - margin_left
        page_bottom = 2.5 * cm

        def new_page(y):
            p.showPage()
            p.setFont('Helvetica', 10)
            return height - 2 * cm

        # ===== HEADER SECTION =====
        y = height - 1.5 * cm

        # School/Board header line
        p.setFont('Helvetica-Bold', 12)
        p.drawCentredString(width / 2, y, paper.board or 'Board of Secondary Education')
        y -= 18

        # Title
        p.setFont('Helvetica-Bold', 16)
        title = paper.title or f'{paper.subject} Examination Paper'
        p.drawCentredString(width / 2, y, title)
        y -= 20

        # Subject / Class / Meta info
        p.setFont('Helvetica', 10)
        p.drawCentredString(width / 2, y,
            f'Class: {paper.class_name}  |  Subject: {paper.subject}  |  Difficulty: {paper.difficulty}')
        y -= 16

        p.drawCentredString(width / 2, y, f'Maximum Marks: 80  |  Time Allowed: 3 Hours')
        y -= 12

        # Separator line
        p.setStrokeColorRGB(0.12, 0.23, 0.37)  # Navy
        p.setLineWidth(1.5)
        p.line(margin_left, y, margin_right, y)
        y -= 8

        # General instructions
        p.setFont('Helvetica-Bold', 9)
        p.drawString(margin_left, y, 'General Instructions:')
        y -= 14
        p.setFont('Helvetica', 8)
        instructions = [
            '1. All questions are compulsory unless otherwise stated.',
            '2. Marks are indicated against each question.',
            '3. Write neat and legible answers.',
        ]
        for inst in instructions:
            p.drawString(margin_left + 0.5 * cm, y, inst)
            y -= 12
        y -= 6

        # Thin separator
        p.setLineWidth(0.5)
        p.setStrokeColorRGB(0.7, 0.7, 0.7)
        p.line(margin_left, y, margin_right, y)
        y -= 18

        # ===== PAPER CONTENT =====
        def draw_text_block(text, x, y, font='Helvetica', size=10, max_width=None, line_height=14):
            """Draw text with proper word wrapping and page breaks."""
            if max_width is None:
                max_width = usable_width
            p.setFont(font, size)
            for paragraph in text.split('\n'):
                paragraph = paragraph.strip()
                if not paragraph:
                    y -= line_height * 0.6
                    if y < page_bottom:
                        y = new_page(y)
                    continue

                # Check if this is a section header (all caps or starts with Section/SECTION)
                is_header = (paragraph.isupper() and len(paragraph) < 80) or \
                            paragraph.startswith('Section') or paragraph.startswith('SECTION') or \
                            paragraph.startswith('PART')
                if is_header:
                    y -= 6
                    if y < page_bottom:
                        y = new_page(y)
                    p.setFont('Helvetica-Bold', 11)
                    p.drawString(x, y, paragraph)
                    y -= 4
                    # Draw subtle underline
                    p.setStrokeColorRGB(0.8, 0.72, 0.3)  # Gold
                    p.setLineWidth(0.8)
                    text_w = p.stringWidth(paragraph, 'Helvetica-Bold', 11)
                    p.line(x, y, x + text_w, y)
                    y -= line_height
                    p.setFont(font, size)
                    continue

                # Check if it's a question line (starts with number or Q)
                is_question = len(paragraph) > 0 and (
                    (paragraph[0].isdigit() and '.' in paragraph[:5]) or
                    paragraph.startswith('Q') and len(paragraph) > 1 and (paragraph[1].isdigit() or paragraph[1] == '.')
                )
                if is_question:
                    y -= 4
                    p.setFont('Helvetica-Bold', 10)
                else:
                    p.setFont(font, size)

                # Word wrap
                words = paragraph.split()
                line = ''
                for word in words:
                    test = f'{line} {word}'.strip()
                    if p.stringWidth(test, p._fontname, p._fontsize) < max_width:
                        line = test
                    else:
                        if y < page_bottom:
                            y = new_page(y)
                        p.drawString(x, y, line)
                        y -= line_height
                        line = word
                if line:
                    if y < page_bottom:
                        y = new_page(y)
                    p.drawString(x, y, line)
                    y -= line_height

                # Reset font after question
                if is_question:
                    p.setFont(font, size)

            return y

        if paper.paper_text:
            y = draw_text_block(paper.paper_text, margin_left, y)

        # ===== FOOTER =====
        y -= 10
        if y < page_bottom + 2 * cm:
            y = new_page(y)
        p.setStrokeColorRGB(0.7, 0.7, 0.7)
        p.setLineWidth(0.5)
        p.line(margin_left, y, margin_right, y)
        y -= 14
        p.setFont('Helvetica-Oblique', 8)
        p.drawCentredString(width / 2, y, '--- End of Paper ---')
        y -= 12
        p.setFont('Helvetica', 7)
        p.drawCentredString(width / 2, y, f'Generated by papersAI | {paper.board} | {paper.class_name} | {paper.subject}')

        p.save()
        buffer.seek(0)

        filename = f"paper_{paper.id}_{paper.subject.replace(' ', '_')}.pdf"
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Get dashboard statistics', tags=['Dashboard'])
    def get(self, request):
        user = request.user
        papers = Paper.objects.filter(teacher=user)
        from apps.students.models import StudentClass

        stats = {
            'papers_generated': papers.filter(status=Paper.STATUS_READY).count(),
            'hours_saved': papers.filter(status=Paper.STATUS_READY).count() * 3,
            'active_classes': StudentClass.objects.filter(teacher=user).count(),
            'recent_papers': PaperListSerializer(papers[:5], many=True).data,
        }
        return Response(stats)
