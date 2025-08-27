from django.urls import reverse
from django.db.models import Max

from datetime import time

from rest_framework import status
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    force_authenticate,
    APIClient,
)

from testing.models import User, ScheduleCalendar, Schedule, DailyEvent

"""
NB: Note that 8 Schedules are automatically created in a ScheduleCalendar
"""


class AuthenticationViewTestCase(APITestCase):
    """Testing authentication works"""

    @classmethod
    def setUpTestData(cls):
        # creating users

        dault = User.objects.create_user(
            username="daultimateboss", password="thechosenone"
        )
        batman = User.objects.create_user(username="batman", password="theshadows")

    def test_correct_credentials_token(self):
        """Test correct credentials results in a 200"""

        response = self.client.post(
            "/api/token/", {"username": "daultimateboss", "password": "thechosenone"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "access")

    def test_incorrect_credentials(self):
        """Test incorrect credentials results in a 404"""

        response = self.client.post(
            "/api/token/", {"username": "daultimateboss", "password": "thechosene"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ScheduleCalendarListViewTestCase(APITestCase):
    """Testing schedule calendar list / creating new schedule calendar"""

    @classmethod
    def setUpTestData(cls):
        # creating users

        # dont forget a default calendar is auto created
        dault = User.objects.create_user(
            username="daultimateboss", password="thechosenone"
        )
        batman = User.objects.create_user(username="batman", password="theshadows")

        # creating calendars
        daults_daily_calendar = ScheduleCalendar.objects.create(
            name="Daily Calendar", owner=dault
        )

        daults_school_calendar = ScheduleCalendar.objects.create(
            name="School calendar", owner=dault
        )

        batman_gotham_calendar = ScheduleCalendar.objects.create(
            name="Gotham", owner=batman
        )

        # calendars are auto populated with empty schedules

    def test_schedule_calendar_list_anonymoususer(self):
        """Should return an error as view needs a logged in user"""
        response = self.client.get(reverse("schedulecalendar-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_schedule_calendar_list_loggedin(self):
        """Test appropriate calendars are returned for logged in user"""
        user = User.objects.get(username="daultimateboss")
        self.client.force_authenticate(user=user)

        response = self.client.get(
            reverse("schedulecalendar-list"),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_calendar(self):
        """Test calendars are created"""
        user = User.objects.get(username="daultimateboss")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("schedulecalendar-list"), {"name": "Gym Calendar"}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["object"]["name"], "Gym Calendar")
        self.assertEqual(user.schedule_cals.all().count(), 4)

    def test_invalid_data(self):
        """Test appropriate response message is sent"""
        user = User.objects.get(username="daultimateboss")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("schedulecalendar-list"), {"nae": "Gym Calendar"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # creating users
        dault = User.objects.create_user(
            username="daultimateboss", password="thechosenone"
        )
        batman = User.objects.create_user(username="batman", password="theshadows")

        # creating calendars
        daults_daily_calendar = ScheduleCalendar.objects.create(
            name="Daily Calendar", owner=dault
        )
        daults_school_calendar = ScheduleCalendar.objects.create(
            name="School Calendar", owner=dault
        )

        batman_gotham_calendar = ScheduleCalendar.objects.create(
            name="Gotham", owner=batman
        )

        cls.owner = dault
        cls.other_owner = batman
        cls.main_calendar = daults_daily_calendar
        cls.main_id = daults_daily_calendar.id
        # anonymous user
        cls.other_client = APIClient()
        cls.batman_client = APIClient()

    def setUp(self):
        self.client.force_authenticate(user=self.owner)


class ScheduleCalendarItemViewTestCase(GenTest):
    def test_get_rightowner_calendarexists(self):
        """Test proper calendar is returned"""
        calendar = ScheduleCalendar.objects.get(owner=self.owner, name="Daily Calendar")
        response = self.client.get(reverse("schedulecalendar-item", args=[calendar.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Daily Calendar")

    def test_get_wrongowner_calendarexists(self):
        """Test appropriate response is returned"""
        calendar = ScheduleCalendar.objects.get(owner=self.other_owner, name="Gotham")

        response = self.client.get(reverse("schedulecalendar-item", args=[calendar.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_rightowner_calendarnotexists(self):
        """Test appropriate response is returned when calendar doenst exist"""
        bad_calendar_id = (
            ScheduleCalendar.objects.all().aggregate(Max("id"))["id__max"] + 1
        )

        response = self.client.get(
            reverse("schedulecalendar-item", args=[bad_calendar_id])
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_changing_name_validdata(self):
        """Test put endpoint"""
        cal_id = ScheduleCalendar.objects.get(
            owner=self.owner, name="School Calendar"
        ).id

        response = self.client.put(
            reverse("schedulecalendar-item", args=[cal_id]),
            data={"name": "Gym Calendar"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["object"]["name"], "Gym Calendar")

    def test_put_changing_name_invalid_data(self):
        """Ensure appropriate response is returned"""

        cal_id = ScheduleCalendar.objects.get(
            owner=self.owner, name="School Calendar"
        ).id

        response = self.client.put(
            reverse("schedulecalendar-item", args=[cal_id]),
            data={"nam": "Gym Calendar"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_valid_id(self):
        """Ensure ability to delete calendars"""

        cal_id = ScheduleCalendar.objects.get(
            owner=self.owner, name="School Calendar"
        ).id

        response = self.client.delete(reverse("schedulecalendar-item", args=[cal_id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Calendar deleted")


class ScheduleListView(GenTest):
    """Testing ScheduleListView"""

    def test_get_schedules_of_calendar_of_anonymous_user(self):
        """Test appropriate reponse is returned"""

        response = self.other_client.get(reverse("schedule-list", args=[self.main_id]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_schedules_of_calendar_of_logged_in_user(self):
        """Test all schedules in a calendar are returned"""

        response = self.client.get(reverse("schedule-list", args=[self.main_id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 8 calendars are created by default
        self.assertEqual(len(response.json()), 8)

    def test_create_schedule_with_appropriate_data(self):
        response = self.client.post(
            reverse("schedule-list", args=[self.main_id]),
            data={"name": "0", "value": "2"},
        )
        res = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res["name"], "0")
        self.assertEqual(res["value"], 2)
        self.assertEqual(res["calendar"]["name"], "Daily Calendar")
        self.assertEqual(self.main_calendar.schedules_set.count(), 9)

    def test_create_schedule_that_already_exists(self):
        """Test appropriate response if you try to create a schedule that exists"""
        response = self.client.post(
            reverse("schedule-list", args=[self.main_id]),
            data={"name": "0", "value": 1},
        )

        res = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res["message"], "Schedule already exists")

    def test_create_schedule_inappropriate_data(self):
        """Test appropriate response returned if inappropriate data is used to create schedule"""

        response = self.client.post(
            reverse("schedule-list", args=[self.main_id]),
            data={"name": "9", "value": "4"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_accept_post_and_get(self):
        """Test appropriate response returned if not post or get request sent to view"""

        response = self.client.patch(reverse("schedule-list", args=[self.main_id]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(reverse("schedule-list", args=[self.main_id]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(reverse("schedule-list", args=[self.main_id]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EventGenTest(GenTest):

    """create and get events with save caveats"""

    @classmethod
    def setUpTestData(cls):
        # creating users
        super().setUpTestData()

        # unique monday schedule
        dault_daily_monday = Schedule.objects.get(
            name="0", calendar=cls.main_calendar, value="1"
        )

        # adding some events
        sleep = DailyEvent.objects.create(
            title="Sleep",
            start_time=time(0, 0),
            end_time=time(6, 30),
            schedule=dault_daily_monday,
        )
        work = DailyEvent.objects.create(
            title="Work",
            start_time=time(9, 30),
            end_time=time(11, 30),
            schedule=dault_daily_monday,
        )

        cls.main_schedule = dault_daily_monday.id
        cls.work = work

    def setUp(self):
        self.client.force_authenticate(user=self.owner)


class EventListView(EventGenTest):
    def test_get_event_loggedin_user(self):
        response = self.client.get(reverse("event-list", args=[self.main_schedule]))
        # only two events have been created so far
        self.assertEqual(len(response.json()), 2)

    def test_get_event_anonymous_user(self):
        response = self.other_client.get(
            reverse("event-list", args=[self.main_schedule])
        )
        # only two events have been created so far
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_event_that_is_not_yours(self):
        self.batman_client.force_authenticate(self.other_owner)
        response = self.batman_client.get(
            reverse("event-list", args=[self.main_schedule])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_appropriate_data_owner_schedule_sequential_event(self):
        response = self.client.post(
            reverse("event-list", args=[self.main_schedule]),
            data={"title": "Play", "start_time": "11:30", "end_time": "12:30"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailyEvent.objects.count(), 3)
        self.assertEqual(response.json()["object"]["title"], "Play")

    def test_post_appropriate_data_owner_schedule_sequential_event_that_overlaps(self):
        response = self.client.post(
            reverse("event-list", args=[self.main_schedule]),
            data={"title": "Play", "start_time": "11:20", "end_time": "12:30"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DailyEvent.objects.count(), 2)
        self.assertEqual(response.json()["message"], "Invalid times")

    def test_post_appropriate_data_owner_schedule_overlap_event(self):
        response = self.client.post(
            reverse("event-list", args=[self.main_schedule]),
            data={
                "title": "Play",
                "start_time": "11:20",
                "end_time": "12:30",
                "overlap": "on",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailyEvent.objects.count(), 3)
        self.assertEqual(response.json()["object"]["title"], "Play")

        self.assertEqual(
            DailyEvent.objects.get(
                schedule=self.main_schedule,
                title="Work",
            ).start_time,
            time(9, 20),
        )  # this event should have been pushed back by 10mins initial time was 9:30 now 9:20

    """        T#o test
#
t#est crud  of calendars
c#rud of schedules
c#rud of events
#
creation of schedules when calendar is created
all apis"""
