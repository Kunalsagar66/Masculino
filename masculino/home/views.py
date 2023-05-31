from django.http import HttpResponse
from django.shortcuts import render

import logging
# Create your views here.
def home(request):
    logging.info("****************************** Home View ******************************")
    try:
        return render(request,'home/home.html')
    except Exception as error:
        logging.error(f'Error in get_log function : {str(error)}')
