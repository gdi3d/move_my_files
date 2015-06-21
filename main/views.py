from django.shortcuts import render
from django.contrib.auth.models import User, Group
from main.models import Connection
#from django.http import HttpResponse

#from django.template import RequestContext
from django.contrib.auth.decorators import login_required

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    #context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold font from the context"}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    #return render_to_response('main/index.html', context_dict, context)
    return render(request, 'main/index.html', context_dict)