from django.db import models

class Band(models.Model):
    band_id = models.AutoField(primary_key=True, db_column='band_id')
    band_name = models.CharField("Название группы", max_length=100)
    genre = models.CharField("Жанр", max_length=50)
    founded_date = models.DateTimeField("Дата основания")

    class Meta:
        db_table = "bands"
        managed = False

    def __str__(self):
        return self.band_name

class Concert(models.Model):
    concert_id = models.AutoField(primary_key=True, db_column='concert_id')
    concert_title = models.CharField("Название", max_length=200)
    venue_address = models.CharField("Адрес", max_length=255)
    concert_date = models.DateTimeField("Дата и время")

    class Meta:
        db_table = "concerts"
        managed = False

    def __str__(self):
        return self.concert_title

class Performance(models.Model):
    performance_id = models.AutoField(primary_key=True, db_column='performance_id')
    band = models.ForeignKey(Band, on_delete=models.DO_NOTHING, db_column='band_id')
    concert = models.ForeignKey(Concert, on_delete=models.DO_NOTHING, db_column='concert_id', related_name='performances')
    performance_order = models.IntegerField("Порядок выступления")

    class Meta:
        db_table = "performances"
        managed = False

    def __str__(self):
        return f"Выступление {self.performance_id} на {self.concert.concert_title}"