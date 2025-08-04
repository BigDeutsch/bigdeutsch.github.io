from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
import markdown2
from . import util
from random import choice

class NewWikiForm(forms.Form):
    title = forms.CharField(
        label="Title",  
        label_suffix="",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Page Title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Insert Content in Markdown Notation'}), required=True, label="Content", label_suffix="")

class EditWikiForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="Content", label_suffix="")    

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    return render(request, "encyclopedia/title.html", {
        "title": title,
        "content": markdown2.markdown(util.get_entry(title))
    })
def addpage(request):
    if request.method == "GET":
        return render(request, "encyclopedia/addpage.html", {
        "entries": util.list_entries(),
        "form": NewWikiForm()
        })
    elif request.method == "POST":
        form = NewWikiForm(request.POST)
        entries = util.list_entries()
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in entries:
                form.add_error("title", "An entry with this title already exists.")
                return render(request, "encyclopedia/addpage.html", {
                    "entries": util.list_entries(),
                    "form": form
                })
            else:
                util.save_entry(title, content)
                return redirect(reverse("wiki:index"))
        return redirect(reverse("wiki:index"))
    
def edit(request, title):
    if request.method == "GET":
        return render(request, "encyclopedia/edit.html", {
            "title": title,
             "form": EditWikiForm(initial={
                 "content": util.get_entry(title)
                 })
      })
    else:
        form = EditWikiForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect(reverse("wiki:entry", kwargs={"title": title}))
        else:
            return render(request,"encyclopedia/edit.html", {
                "title": title,
                "form": form
            })


def search(request):
    if request.method == "POST":
        query = request.POST.get("q").lower()
        entries = util.list_entries()
        results = []
        for entry in entries:
            if query == entry.lower():
                return redirect(reverse('wiki:entry', kwargs={"title": entry}))
            elif query in entry.lower():
                results.append(entry)
        return render(request, "encyclopedia/search.html", {
            "query": query,
            "results": results,
            "count": len(results)
    })
def random(request):
    random_page = choice(util.list_entries())
    return redirect(reverse('wiki:entry', kwargs={"title": random_page}))
