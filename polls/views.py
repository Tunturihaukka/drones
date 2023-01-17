from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.forms.models import model_to_dict
from django.utils import timezone
import json
import numpy as np
import urllib3 as ulib
from bs4 import BeautifulSoup as bs

from polls.models import Person


# This function is called when the homepage is requested. 
def drones(request):
    
    # Initializing the homepage with the template when page is first requested.
    if not (request.content_type == 'application/json'):
        return render(request, 'home.html')

    # Modifying the homepage when Ajax requests JsonResponse to list the rule breaking users
    http = ulib.PoolManager()
    response = http.request('GET', 'http://assignments.reaktor.com/birdnest/drones')
    soup = bs(response.data, "xml") # Pushing drone data to be handled with BeautifulSoup
    bs_drones = soup.find_all('drone') # Extracting every drone from the xml data

    

    for drone in bs_drones: # Handling drone-by-drone
        drone_x = float(drone.find('positionX').get_text(strip=True))
        drone_y = float(drone.find('positionY').get_text(strip=True))

        # Computing distance between the drone and the bird
        drone_loc = np.sqrt(np.power(drone_x-250000.0 , 2)+np.power(drone_y-250000.0 , 2))
        if (drone_loc > 100000.0): # Moving to the next drone if no-go area was not entered
            continue
        
        # Requesting the info for rule violating drone users
        serial_number = drone.find('serialNumber').get_text(strip=True) 
        info_url = 'http://assignments.reaktor.com/birdnest/pilots/'
        id_response = http.request('GET', info_url + serial_number)

        # Not considering further if drone had no registered user
        if (id_response.status == 404):
            continue

        # Extracting info of the registered user of the violating drone
        parsed_json = json.loads(id_response.data)
        name_found = parsed_json['firstName'] + " " + parsed_json['lastName']
        phone_found = parsed_json['phoneNumber']
        email_found = parsed_json['email']

        # If user exists already in the database, checking if closest distance
        # needs to updated.
        if (Person.objects.filter(name=name_found)).exists():
            person_object = Person.objects.get(name=name_found)
            distance_database = float(person_object.closest_distance_in_meters)*1000.0
            distance_now = drone_loc
            shortest_distance = np.minimum(distance_now, distance_database)

            person = Person(name=name_found, last_seen_date = timezone.now(),
                            phone=phone_found, email=email_found,
                            closest_distance_in_meters=shortest_distance/1000.0)
            person.save()

        # A new violating user will be added to the database
        else:
            current_distance = drone_loc
            person = Person(name=name_found, last_seen_date = timezone.now(),
                            phone=phone_found, email=email_found,
                            closest_distance_in_meters=current_distance/1000.0)
            person.save()

    # Deleting from database users whose latest violation was over 10 minutes ago
    detections = list(Person.objects.values())
    recently_detected = {item['name']:item for item in detections}
    time_treshold = timezone.now()-timezone.timedelta(minutes=10)
    Person.objects.exclude(last_seen_date__gt=time_treshold).delete()
    
    # Returning current database to the requesting Ajax function in JSON form
    return JsonResponse(recently_detected)
        









