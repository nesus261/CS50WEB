from django import forms
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from random import randint
import markdown2
import re

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    content = util.get_entry(entry)
    if content:
        return render(request, "encyclopedia/wiki.html", {
            "title": entry,
            "content": markdown(content) 
        })
    else: 
        return render(request, "encyclopedia/wiki.html", {
            "title": "Not found",
            "content": f"Not found entry for {entry}"
        })

def search(request):
    q = request.POST.get('q')
    if util.get_entry(q): 
        return HttpResponseRedirect(reverse("wiki", kwargs={ 'entry': q }))
    entries = list(filter(lambda entry: q.lower() in entry.lower(), util.list_entries()))
    return render(request, "encyclopedia/search.html", {
        "entries": entries
    })

class PageForm(forms.Form):
    title = forms.CharField(label="Title", min_length=1)
    content = forms.CharField(widget=forms.Textarea, label="Content", min_length=1)

def new_page(request):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if util.get_entry(title): #.lower() in [entry.lower() for entry in util.list_entries()]:
                messages.error(request, f"{title} already exist in wiki!")
            else:
                util.save_entry(title,form.cleaned_data["content"])
                return HttpResponseRedirect(reverse("wiki", kwargs={ 'entry': title }))
    return render(request, "encyclopedia/new_page.html", {
        "form": PageForm()
    })

def edit_page(request, entry):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if util.get_entry(title):
                util.save_entry(title, form.cleaned_data["content"])
                return HttpResponseRedirect(reverse("wiki", kwargs={ 'entry': title }))
            else:
                messages.error(request, f"{title} doesn't exist in wiki!")
    return render(request, "encyclopedia/edit_page.html", {
        "form": PageForm(initial={'title': entry, 'content': util.get_entry(entry)}),
        "entry": entry
    })

def random_page(request):
    entries = util.list_entries()
    entry = entries[randint(0, len(entries)-1)]
    return HttpResponseRedirect(reverse("wiki", kwargs={ 'entry': entry }))

def markdown(text):
    return markdown2.markdown(text)
    # Headings 
    for i in range(6, 0, -1):
        text = re.sub("#"*i + rf" (.*?)\n", rf"<h{i}>\1</h{i}>\n",text)
    # Bold 
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # Unordered lists
    # first convert * to li
    text = re.sub(r"\* (.*?)\n", r"<li>\1</li>", text)
    # second add ul tag 
    text = re.sub("\n\n<li>(.*?)</li>\n", r"\n<ul><li>\1</li></ul>\n\n", text)
    # Links 
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href='\2'>\1</a>", text)
    # Paragraphs 
    text = re.sub(r"\n\n(.+?)\n", r"<p>\1</p>\n", text)
    return text
