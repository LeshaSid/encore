from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Musician(models.Model):
    INSTRUMENT_CHOICES = [
        ('guitar', 'Guitar'),
        ('bass', 'Bass'),
        ('drums', 'Drums'),
        ('keyboards', 'Keyboards'),
        ('piano', 'Piano'),
        ('vocals', 'Vocals'),
        ('violin', 'Violin'),
        ('cello', 'Cello'),
        ('trumpet', 'Trumpet'),
        ('saxophone', 'Saxophone'),
        ('trombone', 'Trombone'),
        ('flute', 'Flute'),
        ('clarinet', 'Clarinet'),
        ('accordion', 'Accordion'),
        ('harp', 'Harp'),
    ]
    
    musician_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+375[0-9]{9}$',
                message='Phone must be in format +375XXXXXXXXX'
            )
        ]
    )
    telegram = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^@.+',
                message='Telegram must start with @'
            )
        ]
    )
    instrument = models.CharField(max_length=50, choices=INSTRUMENT_CHOICES)
    
    class Meta:
        db_table = 'musicians'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.instrument})"


class Band(models.Model):
    GENRE_CHOICES = [
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('jazz', 'Jazz'),
        ('blues', 'Blues'),
        ('classical', 'Classical'),
        ('electronic', 'Electronic'),
        ('folk', 'Folk'),
        ('metal', 'Metal'),
        ('punk', 'Punk'),
        ('reggae', 'Reggae'),
        ('hip-hop', 'Hip-Hop'),
        ('country', 'Country'),
        ('funk', 'Funk'),
        ('soul', 'Soul'),
        ('r&b', 'R&B'),
        ('alternative', 'Alternative'),
        ('indie', 'Indie'),
        ('hard_rock', 'Hard Rock'),
        ('progressive', 'Progressive'),
        ('house', 'House'),
        ('techno', 'Techno'),
    ]
    
    band_id = models.AutoField(primary_key=True)
    band_name = models.CharField(max_length=100)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    founded_date = models.DateField(default=timezone.now)
    # Поле для логотипа
    logo = models.ImageField(upload_to='band_logos/', blank=True, null=True, verbose_name='Логотип')
    
    class Meta:
        db_table = 'bands'
    
    def __str__(self):
        return f"{self.band_name} ({self.genre})"


class Concert(models.Model):
    concert_id = models.AutoField(primary_key=True)
    concert_title = models.CharField(max_length=200)
    venue_address = models.CharField(max_length=255)
    concert_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'concerts'
    
    def __str__(self):
        return f"{self.concert_title} at {self.venue_address}"


class Performance(models.Model):
    performance_id = models.AutoField(primary_key=True)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, db_column='band_id')
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, db_column='concert_id')
    performance_order = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'performances'
    
    def __str__(self):
        return f"{self.band} at {self.concert} (order: {self.performance_order})"


class Rehearsal(models.Model):
    rehearsal_id = models.AutoField(primary_key=True)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, db_column='band_id')
    rehearsal_date = models.DateTimeField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'rehearsals'
    
    def __str__(self):
        return f"{self.band} rehearsal at {self.location}"


class BandMembership(models.Model):
    band = models.ForeignKey(Band, on_delete=models.CASCADE, db_column='band_id')
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, db_column='musician_id')
    join_date = models.DateField(default=timezone.now)
    
    class Meta:
        db_table = 'band_membership'
        unique_together = ('band', 'musician')
    
    def __str__(self):
        return f"{self.musician} in {self.band} since {self.join_date}"