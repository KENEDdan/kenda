from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Kenda — The Study Platform'
        ctx['features'] = [
            {
                'icon': 'bi-people-fill',
                'title': 'Student Management',
                'desc': 'Enrol, track, and manage every student from admission to graduation.',
            },
            {
                'icon': 'bi-journal-check',
                'title': 'Academic Records',
                'desc': 'Grades, transcripts, attendance — all in one place, always accurate.',
            },
            {
                'icon': 'bi-cash-stack',
                'title': 'Fee Management',
                'desc': 'Invoices, payments, and reminders handled automatically.',
            },
            {
                'icon': 'bi-calendar3',
                'title': 'Timetables',
                'desc': 'Smart scheduling for classes, exams, and school events.',
            },
            {
                'icon': 'bi-chat-dots-fill',
                'title': 'Communication',
                'desc': 'Notify parents, teachers, and students via SMS and email instantly.',
            },
            {
                'icon': 'bi-bar-chart-fill',
                'title': 'Reports & Analytics',
                'desc': 'Data-driven insights to help school leaders make better decisions.',
            },
        ]
        ctx['plans'] = [
            {
                'name': 'Starter',
                'price': '$49',
                'period': '/month',
                'desc': 'Perfect for small schools getting started.',
                'features': ['Up to 300 students', '5 staff accounts', 'Core modules', 'Email support'],
                'cta': 'Get Started',
                'highlighted': False,
            },
            {
                'name': 'Growth',
                'price': '$129',
                'period': '/month',
                'desc': 'For growing schools that need more power.',
                'features': ['Up to 1,000 students', '25 staff accounts', 'All modules', 'SMS notifications', 'Priority support'],
                'cta': 'Start Free Trial',
                'highlighted': True,
            },
            {
                'name': 'Enterprise',
                'price': 'Custom',
                'period': '',
                'desc': 'For large institutions and school networks.',
                'features': ['Unlimited students', 'Unlimited staff', 'Custom integrations', 'Dedicated support', 'On-premise option'],
                'cta': 'Contact Us',
                'highlighted': False,
            },
        ]
        return ctx