from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, RegexValidator


# Create your models here.

# --- client creation choices --- #

PERSON = "person"
PET = "pet"

SPECIES_TYPE_CHOICES = [
    (PERSON, "Person"),
    (PET, "Pet"),
]


MALE = "male"
FEMALE = "female"

GENDER_TYPE_CHOICES = [
    (MALE, "Male"),
    (FEMALE, "Female"),
]



# --- client worksheet choices --- #

OPEN = "open"
CLOSED_TO_OPEN = "closed_to_open"
SEE_NOTES = "see_notes"

CHAKRA_TYPE_CHOICES = [
    (OPEN, "O"),
    (CLOSED_TO_OPEN, "C > O"),
    (SEE_NOTES, "See Notes"),
]


# |===========================|
# |-----  CLASSES BELOW  -----|
# |===========================|



# === USER CLASS === #
User = settings.AUTH_USER_MODEL




# === PROFILE CLASS === #
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return self.user.username
    
    @property
    def user_client(self):
        return self.clients.get(is_user=True)




# === CLIENT CLASS === #
class Client(models.Model):
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="clients") # profile.clients.all()

    first_name = models.CharField(max_length=15, null=True)
    last_name = models.CharField(max_length=30, null=True)
    person_or_pet = models.CharField(
        max_length=20,
        choices=SPECIES_TYPE_CHOICES, # see 'client creation choices' top of this file
        default="person"
    )
    species = models.CharField(max_length=20, null=True)
    gender = models.CharField(
        choices=GENDER_TYPE_CHOICES, # see 'client creation choices' top of this file
        null=True,
        default="",
    )
    is_user=models.BooleanField(default=False, editable=False)
    is_active=models.BooleanField(default=True, editable=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


# === LOCATION CLASS === #
class Location(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="locations") # profile.location.all()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="locations") # client.locations.all()

    street = models.CharField(max_length=30)
    street_ext = models.CharField(max_length=10)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=10)

    def __str__(self):
        street_ext = f"{self.street_ext}" if self.street_ext else ""
        return f"{self.street}\n{street_ext}\n{self.city}, {self.state} {self.zip}\n{self.country}"
    



# === CLIENT WORKSHEET === #
class Client_Worksheet(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="c_worksheets")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="c_worksheets")

    date = models.DateField

    s1 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])
    m1 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])
    e1 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])
    p1 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])

    chakras = models.CharField(
        max_length=20,
        choices=CHAKRA_TYPE_CHOICES, # see 'client worksheet choices' top of this file
        default="open"
    )

    cords = models.BooleanField(default=False)
    how_many = models.PositiveIntegerField(blank=True, null=True)
    to_whom = models.CharField(max_length=50, blank=True, null=True)

#    hindrances = models.BooleanField(default=False)
    dark_ents = models.BooleanField(default=False)
    attacks = models.BooleanField(default=False)
    societal = models.BooleanField(default=False)
    infections = models.BooleanField(default=False)

    s2 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])
    m2 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])
    e2 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])
    p2 = models.PositiveIntegerField(validators=[MaxValueValidator(999999)])

    @property
    def t1(self):
        return self.s1 + self.m1 + self.e1 + self.p1
    
    @property
    def t2(self):
        return self.s2 + self.m2 + self.e2 + self.p2
    
    @property
    def percent_change(self):
        return ((self.t2 - self.t1) / self.t1)
    



# === LOCATION WORKSHEET === #
class Location_Worksheet(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="l_worksheets")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="l_worksheets")

    date = models.DateField

#    issues = models.BooleanField(default=False)
    unwanted_energies = models.BooleanField(default=False)
    stuck_souls = models.BooleanField(default=False)
    portals = models.BooleanField(default=False)

    protection = models.BooleanField(default=False)




# === NOTES CLASS === #
class Notes(models.Model):

    c_worksheet = models.ForeignKey(Client_Worksheet, on_delete=models.CASCADE, related_name="notes")
    l_worksheet = models.ForeignKey(Location_Worksheet, on_delete=models.CASCADE, related_name="notes")

    notes = models.TextField(null=True, blank=True)