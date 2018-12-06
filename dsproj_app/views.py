from django.shortcuts import render
from django.http import HttpResponse
from os import environ


class View:
    def __init__(self):
        self.view = environ.get("VIEW").split(",")

    def get(self):
        return self.view

    def filter(self, filter):
        if filter in self.view:
            return self.view.remove(filter)
        else:
            return ["VIEW ERROR"]


__View__ = View().get()
# Create your views here.


def index(request):
    return HttpResponse('Egan Juan Suhas Alston CMPS128 ASG2')


def get_array_views(filter=None):
    if filter != None:
        print(filter)
    return environ.get("VIEW").split(",")


def get_index_of_target_in_views(ip_port):
    return environ.get("VIEW").split(",").index(ip_port)
