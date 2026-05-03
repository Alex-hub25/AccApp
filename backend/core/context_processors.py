def active_company(request):
    """Inject active_company and user's companies into every template context."""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {
                'active_company': profile.active_company,
                'user_companies': request.user.companies.all(),
            }
        except Exception:
            pass
    return {'active_company': None, 'user_companies': []}
