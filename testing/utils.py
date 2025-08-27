from datetime import datetime, date, timedelta, time
import copy

def is_good_event(event, other_events):
    for other_event in other_events:
        if (
            event.start_time == other_event.start_time
            or event.end_time == other_event.end_time
            or other_event.start_time < event.start_time < other_event.end_time
            or other_event.start_time < event.end_time < other_event.end_time
        ):
            raise ValueError("Bad times")  # describe this

    # if the end_time is less than the start_time ie start something today and end tomorrow return false
    if event.start_time >= event.end_time:
        raise ValueError("Bad times")  # describe this

    return True

def subtract_times(first_time, second_time, delta_or_time=None):
    """return subtraction of two times"""
    difference = datetime.combine(date.min, first_time) - datetime.combine(date.min, second_time)
    if not delta_or_time:
        if difference < timedelta(0) or difference.days:
            raise ValueError("less than zero time")
        
        seconds = difference.seconds 
        hour = seconds // 3600
        minute = (seconds % 3600) // 60
        second = (seconds % 3600) % 60

        return time(hour, minute, second)
    
    else:
        #there are times i want a delta object so i can represent negative time
        return difference
    
def add_times(first_time, second_time):
    """return addition of two times"""
    #no intrinsic solution for this

    addition = (timedelta(hours=first_time.hour, minutes=first_time.minute, seconds=first_time.second) + timedelta(hours=second_time.hour, minutes=second_time.minute,  seconds=second_time.second))

    seconds = addition.seconds

    if addition.days:
        raise ValueError("more than 1 day sum")
    
    hour = seconds // 3600
    minute = (seconds % 3600) // 60
    seconds = (seconds % 3600) % 60

    try:
        return time(hour, minute, seconds)
    except:
        raise ValueError("This is the problem")

def new_save_with_overlap(event, other_events):
    #straight up copying events so can reset state if things go wrong
    other_events = list(other_events)
    new_copy = copy.deepcopy(other_events)

    restoration_needed = True #
    #other_events should be ordered  
    try:
        #some constants needed 
        zero_time_delta = timedelta(0)
        
        preevent = None
        postevent = None
        preshift = None
        postshift = None    

        previous_queue = [] 
        post_queue = [] 

        #logic here is bcuz times are ordered, when difference switches from positive to negative we have found event before and after
        for i, other_event in enumerate(other_events):
            difference = subtract_times(event.start_time, other_event.start_time, "delta")

            if difference > zero_time_delta:
                preevent = other_event
                previous_queue.append(preevent)

            elif difference < zero_time_delta:
                postevent = other_event
                post_queue = other_events[i+1:]
                break       
            
            else:
                #means start of event is same as start of another event
                #its ambiguous the way to shift such an event
                #no event has been touched yet so just raise error
                restoration_needed = False
                raise ValueError("Ambiguous times")

        #now check if new event overlaps preevent or postevent
        #we already know their start time's relation to new event
        if preevent:
            if event.start_time < preevent.end_time:
                preshift = subtract_times(preevent.end_time, event.start_time)

                #shifting events prior to new event to make space for it
                done = False
                previous_queue.pop() #removing preevent from previous queue

                while not done:
                    #shift preevent backwards
                    try:
                        preevent.start_time =  subtract_times(preevent.start_time, preshift)  
                        preevent.end_time = subtract_times(preevent.end_time, preshift)
                    except ValueError: #if shifted out of range value error is raised
                        raise ValueError
                        
                    preevent.save(bypass=True)

                    if previous_queue:
                        new_prev = previous_queue.pop() #event prior to preevent
                        if preevent.start_time < new_prev.end_time: #if it doesnt need to be shifted we are done else repeat
                            preevent = new_prev
                        
                        else:
                            done = True
                    else:
                        done=True #we have adjusted all already


        if postevent:
            if event.end_time > postevent.start_time:
                postshift = subtract_times(event.end_time, postevent.start_time)

                done = False
                post_queue.reverse() #i think reversing the list then popping from the end might be more efficient overall

                while not done:
                    #shift postevent backwards
                    try:
                        postevent.start_time =  add_times(postevent.start_time, postshift)  
                        postevent.end_time = add_times(postevent.end_time, postshift)
                    #if it goes out of range raise value error add_times raises valueerror
                    except ValueError: 
                        raise ValueError

                    #if it doesnt go out of range
                    postevent.save(bypass=True)

                    if post_queue:
                        new_prev = post_queue.pop() #event prior to postevent
                        if postevent.end_time > new_prev.start_time: #if it no need to be shifted we are done else repeat
                            postevent = new_prev
                            
                        else:
                            done = True
                    else:
                        #we have adjusted all already
                        done=True

        #space has been made for event by now so just save
        event.save(bypass=True)
    
        return True
    
    except Exception as e:
        if restoration_needed:
            #returning to prior state
            for other_event in new_copy:
                other_event.save(bypass=True)

        raise ValueError 