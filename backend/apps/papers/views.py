import io
import os
from django.http import FileResponse
from django.conf import settings
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Paper
from .serializers import PaperListSerializer, PaperDetailSerializer, PaperGenerateSerializer
from .gemini_service import generate_paper
from .curriculum import RTU_BRANCHES, RBSE_CBSE_CLASSES, RBSE_CBSE_SUBJECTS
from apps.subscriptions.models import CreditWallet


class CurriculumOptionsView(APIView):
    """Get curriculum options (branches, semesters, subjects) based on board selection"""
    
    @extend_schema(
        summary='Get curriculum options for a board',
        tags=['Papers'],
        parameters=[
            {'name': 'board', 'in': 'query', 'required': True, 'schema': {'type': 'string'}, 'description': 'Board name (RBSE, RTU, CBSE)'},
            {'name': 'branch', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Branch for RTU (e.g., CSE)'},
            {'name': 'semester', 'in': 'query', 'required': False, 'schema': {'type': 'string'}, 'description': 'Semester for RTU'},
        ]
    )
    def get(self, request):
        board = request.query_params.get('board', 'RBSE')
        branch = request.query_params.get('branch')
        semester = request.query_params.get('semester')
        
        if board == 'RTU':
            # Get RTU curriculum data
            if not branch:
                # Return list of branches
                branches = list(RTU_BRANCHES.keys())
                return Response({
                    'branches': [{'code': code, 'name': data['name']} for code, data in RTU_BRANCHES.items()]
                })
            
            if branch not in RTU_BRANCHES:
                return Response({'error': f'Branch {branch} not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not semester:
                # Return list of semesters for the branch
                branch_data = RTU_BRANCHES[branch]
                semesters = [
                    {'semester': data['semester'], 'totalCredits': data['totalCredits']}
                    for data in sorted(branch_data['semesters'].values(), key=lambda x: x['semester'])
                ]
                return Response({'semesters': semesters})
            
            if semester not in RTU_BRANCHES[branch]['semesters']:
                return Response({'error': f'Semester {semester} not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Return subjects for the semester
            semester_data = RTU_BRANCHES[branch]['semesters'][semester]
            subjects = [
                {'name': name, 'credits': credits}
                for name, credits in semester_data['subjects'].items()
            ]
            return Response({
                'subjects': subjects,
                'totalCredits': semester_data['totalCredits']
            })
        
        elif board in ['RBSE', 'CBSE']:
            # Get standard class/subject structure
            classes = list(RBSE_CBSE_CLASSES.keys())
            if not branch:  # branch parameter used for class_name for RBSE/CBSE
                return Response({'classes': classes})
            
            class_name = branch
            if class_name in RBSE_CBSE_SUBJECTS:
                subjects = RBSE_CBSE_SUBJECTS[class_name]
                return Response({'subjects': subjects})
            
            return Response({'error': f'Class {class_name} not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': f'Board {board} not found'}, status=status.HTTP_400_BAD_REQUEST)


class PaperGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PaperGenerateSerializer,
        summary='Generate a new question paper using AI',
        tags=['Papers'],
    )
    def post(self, request):
        serializer = PaperGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check credits
        wallet, _ = CreditWallet.objects.get_or_create(user=request.user)
        if wallet.balance < 1:
            return Response({'error': 'Insufficient credits'}, status=status.HTTP_402_PAYMENT_REQUIRED)

        data = serializer.validated_data
        paper = Paper.objects.create(
            teacher=request.user,
            board=data['board'],
            class_name=data['class_name'],
            subject=data['subject'],
            difficulty=data.get('difficulty', 'balanced'),
            topics=data.get('topics', ''),
            adhere_marking_scheme=data.get('adhere_marking_scheme', True),
            branch=data.get('branch'),
            semester=data.get('semester'),
            status=Paper.STATUS_GENERATING,
        )

        try:
            language = data.get('language', 'english')
            result = generate_paper(
                board=paper.board,
                class_name=paper.class_name,
                subject=paper.subject,
                difficulty=paper.difficulty,
                topics=paper.topics,
                adhere_scheme=paper.adhere_marking_scheme,
                language=language,
            )
            paper.paper_text = result.get('paper', '')
            paper.answer_key_text = result.get('answer_key', '')
            paper.status = Paper.STATUS_READY
            paper.save()
            wallet.balance -= 1
            wallet.save()

            return Response(PaperDetailSerializer(paper).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            paper.status = Paper.STATUS_FAILED
            paper.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaperDetailView(generics.RetrieveAPIView):
    serializer_class = PaperDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Paper.objects.filter(teacher=self.request.user)


class PaperListView(generics.ListAPIView):
    serializer_class = PaperListSerializer
    permission_classes = [IsAuthenticated]

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

        import re
        from fpdf import FPDF

        font_dir = os.path.join(settings.BASE_DIR, 'apps', 'papers', 'fonts')
        doc_type = request.GET.get('type', 'paper')

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=25)

        # Register fonts
        pdf.add_font('Hind', '', os.path.join(font_dir, 'Hind-Regular.ttf'))
        pdf.add_font('Hind', 'B', os.path.join(font_dir, 'Hind-Bold.ttf'))
        pdf.add_font('NotoSans', '', os.path.join(font_dir, 'NotoSans-Regular.ttf'))
        pdf.add_font('NotoSans', 'B', os.path.join(font_dir, 'NotoSans-Regular.ttf'))
        pdf.add_font('NotoSansMath', '', os.path.join(font_dir, 'NotoSansMath-Regular.ttf'))
        pdf.add_font('NotoSansMath', 'B', os.path.join(font_dir, 'NotoSansMath-Regular.ttf'))

        # Enable HarfBuzz text shaping for Devanagari + fallback for chemistry/math symbols
        pdf.set_text_shaping(True)
        pdf.set_fallback_fonts(['NotoSans', 'NotoSansMath'])

        pdf.add_page()

        # ===== HEADER SECTION =====
        pdf.set_font('Hind', 'B', 12)
        pdf.cell(w=0, text=paper.board or 'Board of Secondary Education', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Title
        title_suffix = 'Answer Key' if doc_type == 'answer_key' else 'Examination Paper'
        title = f'{paper.title} - {title_suffix}' if paper.title else f'{paper.subject} {title_suffix}'
        pdf.set_font('Hind', 'B', 16)
        pdf.cell(w=0, text=title, align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Subject / Class / Meta info
        pdf.set_font('Hind', '', 10)
        pdf.cell(w=0, text=f'Class: {paper.class_name}  |  Subject: {paper.subject}  |  Difficulty: {paper.difficulty}', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.cell(w=0, text='Maximum Marks: 80  |  Time Allowed: 3 Hours', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Separator line
        pdf.set_draw_color(31, 59, 94)
        pdf.set_line_width(0.5)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(3)

        # General instructions
        pdf.set_font('Hind', 'B', 9)
        pdf.cell(text='General Instructions:', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.set_font('Hind', '', 8)
        for inst in [
            '1. All questions are compulsory unless otherwise stated.',
            '2. Marks are indicated against each question.',
            '3. Write neat and legible answers.',
        ]:
            pdf.cell(text=f'   {inst}', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        pdf.ln(2)

        # Thin separator
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(5)

        # ===== PAPER CONTENT =====
        content_text = paper.answer_key_text if doc_type == 'answer_key' else paper.paper_text
        if content_text:
            self._render_content(pdf, content_text)

        # ===== FOOTER =====
        pdf.ln(5)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(3)
        pdf.set_font('Hind', '', 8)
        pdf.cell(w=0, text='--- End of Paper ---', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font('Hind', '', 7)
        pdf.cell(w=0, text=f'Generated by papersAI | {paper.board} | {paper.class_name} | {paper.subject}', align='C', new_x="LMARGIN", new_y="NEXT")

        # Output to buffer
        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)

        prefix = 'answer_key_' if doc_type == 'answer_key' else 'paper_'
        filename = f"{prefix}{paper.id}_{paper.subject.replace(' ', '_')}.pdf"
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def _latex_to_unicode(text):
        """Convert common LaTeX math notation to Unicode characters."""
        import re

        # Subscript and superscript digit maps
        sub_map = str.maketrans('0123456789+-=()aehijklmnoprstuvx', '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ')
        sup_map = str.maketrans('0123456789+-=()aeinorstuvwxyz', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ᵃᵉⁱⁿᵒʳˢᵗᵘᵛʷˣʸᶻ')

        # Greek letter map
        greek = {
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
            r'\epsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ',
            r'\lambda': 'λ', r'\mu': 'μ', r'\nu': 'ν', r'\pi': 'π',
            r'\sigma': 'σ', r'\tau': 'τ', r'\phi': 'φ', r'\omega': 'ω',
            r'\Delta': 'Δ', r'\Sigma': 'Σ', r'\Omega': 'Ω', r'\Pi': 'Π',
            r'\Gamma': 'Γ', r'\Theta': 'Θ', r'\Lambda': 'Λ', r'\Phi': 'Φ',
        }

        # Arrow map
        arrows = {
            r'\rightarrow': '→', r'\leftarrow': '←', r'\to': '→',
            r'\leftrightarrow': '↔', r'\Rightarrow': '⇒',
            r'\Leftrightarrow': '⇔', r'\uparrow': '↑', r'\downarrow': '↓',
            r'\rightleftharpoons': '⇌', r'\leftrightharpoons': '⇌',
        }

        # Other symbols
        symbols = {
            r'\times': '×', r'\div': '÷', r'\pm': '±', r'\mp': '∓',
            r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
            r'\infty': '∞', r'\degree': '°', r'\circ': '°',
        }

        # Process inline math: $...$
        def convert_math(match):
            expr = match.group(1)

            # \sqrt{...} -> √(...)
            expr = re.sub(r'\\sqrt\{([^}]*)\}', r'√(\1)', expr)

            # \frac{a}{b} -> a/b
            expr = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'\1/\2', expr)

            # Replace Greek, arrows, symbols
            for latex, uni in {**greek, **arrows, **symbols}.items():
                expr = expr.replace(latex, uni)

            # Subscripts: _{...} or _X
            def sub_repl(m):
                content = m.group(1) or m.group(2)
                return content.translate(sub_map)
            expr = re.sub(r'_\{([^}]*)\}|_([A-Za-z0-9])', sub_repl, expr)

            # Superscripts: ^{...} or ^X
            def sup_repl(m):
                content = m.group(1) or m.group(2)
                return content.translate(sup_map)
            expr = re.sub(r'\^\{([^}]*)\}|\^([A-Za-z0-9])', sup_repl, expr)

            # Remove remaining braces
            expr = expr.replace('{', '').replace('}', '')

            return expr

        # Replace all $...$ (non-greedy)
        text = re.sub(r'\$([^$]+)\$', convert_math, text)

        # Also replace standalone LaTeX commands outside of $...$
        for latex, uni in {**greek, **arrows, **symbols}.items():
            text = text.replace(latex, uni)

        return text

    def _render_content(self, pdf, text):
        """Render paper content with markdown table support, section headers, and question formatting."""
        # Preprocess: convert LaTeX math to Unicode
        text = self._latex_to_unicode(text)

        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # ---- Markdown Table Block ----
            if line.startswith('|') and line.endswith('|'):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i].strip())
                    i += 1

                data = []
                for row in table_lines:
                    cells = [c.strip() for c in row.split('|')[1:-1]]
                    # Skip separator rows like |---|---|
                    if all(all(ch in '-: ' for ch in c) for c in cells if c):
                        continue
                    if not data:
                        data.append(cells)
                    else:
                        expected = len(data[0])
                        if len(cells) < expected:
                            cells.extend([''] * (expected - len(cells)))
                        elif len(cells) > expected:
                            cells = cells[:expected]
                        data.append(cells)

                if data:
                    pdf.set_font('Hind', '', 10)
                    col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / max(1, len(data[0]))
                    with pdf.table(col_widths=col_w) as table:
                        for row_idx, row_data in enumerate(data):
                            row = table.row()
                            if row_idx == 0:
                                pdf.set_font('Hind', 'B', 10)
                            else:
                                pdf.set_font('Hind', '', 10)
                            for cell_text in row_data:
                                row.cell(cell_text)
                    pdf.ln(4)
                continue

            i += 1

            # ---- Empty line -> small gap ----
            if not line:
                pdf.ln(3)
                continue

            # ---- Section headers (SECTION A, खण्ड अ, PART, etc.) ----
            is_header = (line.isupper() and len(line) < 80) or \
                        line.startswith('Section') or line.startswith('SECTION') or \
                        line.startswith('PART') or line.startswith('खण्ड')
            if is_header:
                pdf.ln(3)
                pdf.set_font('Hind', 'B', 12)
                pdf.cell(text=line, new_x="LMARGIN", new_y="NEXT")
                # Underline
                pdf.set_draw_color(204, 184, 77)
                pdf.set_line_width(0.3)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + pdf.get_string_width(line), pdf.get_y())
                pdf.ln(4)
                continue

            # ---- Question lines (start with number, Q, or प्र) ----
            is_question = (
                (len(line) > 0 and line[0].isdigit() and '.' in line[:5]) or
                (line.startswith('Q') and len(line) > 1 and (line[1].isdigit() or line[1] == '.')) or
                line.startswith('प्र')
            )
            if is_question:
                pdf.ln(2)
                pdf.set_font('Hind', 'B', 10)
                self._draw_wrapped_text(pdf, line)
                pdf.set_font('Hind', '', 10)
            else:
                pdf.set_font('Hind', '', 10)
                self._draw_wrapped_text(pdf, line)

            pdf.ln(1)

    @staticmethod
    def _draw_wrapped_text(pdf, text):
        """Word-wrap text using cell() instead of multi_cell() to preserve fallback font rendering."""
        max_w = pdf.w - pdf.l_margin - pdf.r_margin
        words = text.split(' ')
        line = ''
        for word in words:
            test = f'{line} {word}'.strip() if line else word
            if pdf.get_string_width(test) < max_w:
                line = test
            else:
                if line:
                    pdf.cell(text=line, new_x="LMARGIN", new_y="NEXT")
                line = word
        if line:
            pdf.cell(text=line, new_x="LMARGIN", new_y="NEXT")


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
