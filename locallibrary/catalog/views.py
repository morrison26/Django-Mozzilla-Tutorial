import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from catalog.models import Book, Author, BookInstance, Genre
from catalog.forms import RenewBookForm

class BookListView(generic.ListView):
    model = Book

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by("due_back")

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_all_loaned_books.html'
    paginate_by=10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o')

# Create your views here.
def index(request):
    """View function for home page of site"""

    #generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    #available books (status - 'a')
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()

    #The 'all()' is implied by default
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
          'num_books':num_books
        , 'num_instances': num_instances
        , 'num_instances_available': num_instances_available
        , 'num_authors': num_authors
        , 'num_visits': num_visits
    }

    #Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context = context)

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == "POST":

        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal-date': proposed_renewal_date})

    context = {
          'form': form
        , 'book_instance': book_instance
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields ='__all__'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('books')
