from django.db import models
from django.conf import settings

class Musician(models.Model):
    musician_id = models.AutoField(primary_key=True, db_column='musician_id')
    first_name = models.CharField("Имя", max_length=50, db_column='first_name')
    last_name = models.CharField("Фамилия", max_length=50, db_column='last_name')
    phone = models.CharField("Телефон", max_length=20, db_column='phone')
    telegram = models.CharField("Telegram", max_length=100, blank=True, null=True, db_column='telegram')
    instrument = models.CharField("Инструмент", max_length=50, db_column='instrument')

    class Meta:
        db_table = "musicians"
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Band(models.Model):
    band_id = models.AutoField(primary_key=True, db_column='band_id')
    band_name = models.CharField("Название группы", max_length=100, db_column='band_name')
    genre = models.CharField("Жанр", max_length=50, db_column='genre')
    founded_date = models.DateField("Дата основания", db_column='founded_date')

    class Meta:
        db_table = "bands"
        managed = False

    def __str__(self):
        return self.band_name

class BandMembership(models.Model):
    band = models.ForeignKey(Band, on_delete=models.DO_NOTHING, db_column='band_id')
    musician = models.ForeignKey(Musician, on_delete=models.DO_NOTHING, db_column='musician_id')
    join_date = models.DateField("Дата вступления", db_column='join_date')

    class Meta:
        db_table = "band_membership"
        managed = False

    def __str__(self):
        return f"{self.musician} в {self.band}"

class Concert(models.Model):
    concert_id = models.AutoField(primary_key=True, db_column='concert_id')
    concert_title = models.CharField("Название", max_length=200, db_column='concert_title')
    venue_address = models.CharField("Адрес", max_length=255, db_column='venue_address')
    concert_date = models.DateTimeField("Дата и время", db_column='concert_date')

    class Meta:
        db_table = "concerts"
        managed = False
        ordering = ['-concert_date']

    def __str__(self):
        return self.concert_title

class Performance(models.Model):
    performance_id = models.AutoField(primary_key=True, db_column='performance_id')
    band = models.ForeignKey(Band, on_delete=models.DO_NOTHING, db_column='band_id')
    concert = models.ForeignKey(Concert, on_delete=models.DO_NOTHING, db_column='concert_id', related_name='performances')
    performance_order = models.IntegerField("Порядок выступления", db_column='performance_order')

    class Meta:
        db_table = "performances"
        managed = False

    def __str__(self):
        return f"Выступление {self.performance_id} на {self.concert.concert_title}"

class Rehearsal(models.Model):
    rehearsal_id = models.AutoField(primary_key=True, db_column='rehearsal_id')
    band = models.ForeignKey(Band, on_delete=models.DO_NOTHING, db_column='band_id')
    rehearsal_date = models.DateTimeField("Дата репетиции", db_column='rehearsal_date')
    duration_minutes = models.IntegerField("Длительность (минуты)", db_column='duration_minutes')
    location = models.CharField("Место", max_length=255, db_column='location')

    class Meta:
        db_table = "rehearsals"
        managed = False

    def __str__(self):
        return f"Репетиция {self.band.band_name} на {self.rehearsal_date}"