from django.http import JsonResponse
from django.views import View

class AuthorListView(View):
    def get(self, request):
        # TODO: Implement logic to list authors
        print("hit this")
        return JsonResponse({'authors': []})

class AuthorDetailView(View):
    def get(self, request, author_id):
        # TODO: logic to retrieve details of a specific author
        return JsonResponse({'author_id': author_id, 'name': 'Author Name'})

class AuthorInboxView(View):
    def get(self, request, author_id):
        # TODO: logic to get the inbox for a specific author
        return JsonResponse({'inbox': []})
