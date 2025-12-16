# booking/models.py
from django.db import models


class Rehearsals(models.Model):
    # Используем те же имена полей, что и в core/models.py
    rehearsal_id = models.AutoField(primary_key=True, db_column='rehearsal_id')
    band_id = models.IntegerField("band id")
    rehearsal_date = models.DateTimeField("Date & time")
    duration_minutes = models.IntegerField("Duration minutes")  # Изменено на duration_minutes
    location = models.CharField("Location", max_length=255)

    class Meta():
        db_table = "rehearsals"
        managed = False

    def __str__(self):
        return f"Rehearsal {self.rehearsal_id} on {self.rehearsal_date}"
    

class Bands(models.Model):
    band_id = models.AutoField(primary_key=True, db_column='band_id')
    band_name = models.CharField("Band name", max_length=100)
    genre = models.CharField("Genre", max_length=50)  # Исправлено
    founded_date = models.DateTimeField("Founded")

    class Meta():
        db_table = "bands"
        managed = False

    def __str__(self):
        return self.band_name
    

class Band_membership(models.Model):
    id = models.BigAutoField(primary_key=True)
    band_id = models.IntegerField("Band id")
    musician_id = models.IntegerField("Musician id")
    join_date = models.DateTimeField("Joined")

    class Meta():
        db_table = "band_membership"
        managed = False

    def __str__(self):
        return f"Membership {self.id}"
    

class Musicians(models.Model):
    musician_id = models.AutoField(primary_key=True, db_column='musician_id')
    first_name = models.CharField("First name", max_length=50)
    last_name = models.CharField("Last name", max_length=50)
    phone = models.CharField("Phone", max_length=20)
    telegram = models.CharField("Telegram", max_length=100)
    instrument = models.CharField("Instrument", max_length=100)

    class Meta():
        db_table = "musicians"
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Performances(models.Model):
    performance_id = models.AutoField(primary_key=True, db_column='performance_id')
    band_id = models.IntegerField("Band id")
    concert_id = models.IntegerField("Concert id")
    performance_order = models.IntegerField("Performance order")

    class Meta():
        db_table = "performances"
        managed = False

    def __str__(self):
        return f"Performance {self.performance_id}"
    

class Concerts(models.Model):
    concert_id = models.AutoField(primary_key=True, db_column='concert_id')
    concert_title = models.CharField("Title", max_length=200)
    venue_address = models.CharField("Address", max_length=255)
    concert_date = models.DateTimeField("Date")

    class Meta():
        db_table = "concerts"
        managed = False

    def __str__(self):
        return self.concert_title