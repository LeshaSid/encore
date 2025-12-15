from django.db import models
from django.utils import timezone

class Musician(models.Model):
    musician_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, null=True)
    telegram = models.CharField(max_length=100, blank=True, null=True)
    instrument = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'musicians'
        managed = False  # Не создавать таблицу, она уже существует

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Band(models.Model):
    band_id = models.AutoField(primary_key=True)
    band_name = models.CharField(max_length=100)
    genre = models.CharField(max_length=50, blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'bands'
        managed = False

    def __str__(self):
        return self.band_name


class Concert(models.Model):
    concert_id = models.AutoField(primary_key=True)
    concert_title = models.CharField(max_length=200)
    venue_address = models.CharField(max_length=255)
    concert_date = models.DateTimeField()

    class Meta:
        db_table = 'concerts'
        managed = False
        ordering = ['concert_date']

    def __str__(self):
        return self.concert_title
    
    def is_upcoming(self):
        return self.concert_date > timezone.now()


class Performance(models.Model):
    performance_id = models.AutoField(primary_key=True)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, db_column='band_id')
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, db_column='concert_id')
    performance_order = models.IntegerField()

    class Meta:
        db_table = 'performances'
        managed = False


class BandMembership(models.Model):
    band = models.ForeignKey(Band, on_delete=models.CASCADE, db_column='band_id')
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, db_column='musician_id')
    join_date = models.DateField()

    class Meta:
        db_table = 'band_membership'
        managed = False
        unique_together = ('band', 'musician')


class Rehearsal(models.Model):
    rehearsal_id = models.AutoField(primary_key=True)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, db_column='band_id')
    rehearsal_date = models.DateTimeField()
    duration_minutes = models.IntegerField()
    location = models.CharField(max_length=255)

    class Meta:
        db_table = 'rehearsals'
        managed = False