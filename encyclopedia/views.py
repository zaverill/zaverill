from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from . import util
from django.urls import reverse
from random import choice


from markdown2 import Markdown
markdowner = Markdown()

class NewEntryForm(forms.Form):
    title = forms.CharField(
        required=True,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Title", "class": "mb-4"}
        ),
    )
    content = forms.CharField(
        required=True,
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control mb-4",
                "placeholder": "Content (markdown)",
                "id": "new_content",
            }
        ),
    )

class SearchForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
      "class": "search",
      "placeholder": "Search Page"}))

class EditForm(forms.Form):
  """ Form Class for Editing Entries """
  text = forms.CharField(label='', widget=forms.Textarea(attrs={
      "placeholder": "Using Markdown, enter page content."
    }))


def index(request):
    if request.GET.get('q'):
        search(request, request.GET['q'])
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
    })


def title(request, title):
    wiki_page = util.get_entry(title)

    if (not wiki_page):
        return render(request, "encyclopedia/error.html", {
          "message": "Not Found",
          "status": 404
        })

    html_wiki_page = markdowner.convert(wiki_page)

    return render(request, "encyclopedia/title.html", {
        "title": title,
        "html_page": html_wiki_page
    })


def search(request):
    query = request.GET.get("q", "")
    if query is None or query == "":
        return render(
            request,
            "encyclopedia/search.html",
            {"found_entries": "", "query": query},
        )

    entries = util.list_entries()

    found_entries = [
        valid_entry
        for valid_entry in entries
        if query.lower() in valid_entry.lower()
    ]
    if len(found_entries) == 1:
        return redirect("title", found_entries[0])

    return render(
        request,
        "encyclopedia/search.html",
        {"found_entries": found_entries, "query": query},
    )


def new(request):
    if request.method == "GET":
        return render(
            request, "encyclopedia/new.html", {"form": NewEntryForm()}
        )

    form = NewEntryForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data.get("title")
        content = form.cleaned_data.get("content")

        if title.lower() in [entry.lower() for entry in util.list_entries()]:
            messages.add_message(
                request,
                messages.WARNING,
                message=f'Entry "{title}" already exists',
            )
        else:
            with open(f"entries/{title}.md", "w") as file:
                file.write(content)
            return redirect("title", title)

    else:
        messages.add_message(
            request, messages.WARNING, message="Invalid request form"
        )

    return render(
        request,
        "encyclopedia/new.html",
        {"form": form},
    )

def edit(request, title):
    if request.method == "GET":
        text = util.get_entry(title)

        return render(request, "encyclopedia/edit.html", {
          "title": title,
          "edit_form": EditForm(initial={'text':text}),
          "search_form": SearchForm()
        })

    elif request.method == "POST":
        form = EditForm(request.POST)

        if form.is_valid():
          text = form.cleaned_data['text']
          util.save_entry(title, text)
          return redirect(reverse('title', args=[title]))

        else:
          return render(request, "encyclopedia/edit.html", {
            "title": title,
            "edit_form": form,
            "search_form": SearchForm()
          })


def random(request):
    entries = util.list_entries()
    selected_choice = choice(entries)
    
    return redirect('title', title=selected_choice)