from django.db import models
from users.models import  CustomUser



class Internship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('approved_by_company', 'Şirket Onayladı'),
        ('approved_by_admin', 'Admin Onayladı'),
        ('rejected', 'Reddedildi'),
        ('completed', 'Tamamlandı'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_internships')
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='company_internships')

    topic = models.CharField(max_length=200, verbose_name="Staj Konusu")
    description = models.TextField(verbose_name="Açıklama", blank=True, null=True)
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    working_days = models.PositiveIntegerField(default=0, verbose_name="Çalışma Günü")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.email} -> {self.company.email} | {self.topic}"

    class Meta:
        verbose_name = "Staj"
        verbose_name_plural = "Stajlar"


class InternshipDiary(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('submitted', 'Gönderildi'),
    ]

    internship = models.ForeignKey('Internship', on_delete=models.CASCADE, related_name='diaries')
    day_number = models.PositiveIntegerField(verbose_name="Gün Numarası")
    content = models.TextField(verbose_name="İçerik")
    date = models.DateField(verbose_name="Tarih")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Durum")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Day {self.day_number} - {self.internship}"

    class Meta:
        verbose_name = "Staj Günlüğü"
        verbose_name_plural = "Staj Günlükleri"
class Evaluation(models.Model):
    internship = models.ForeignKey('Internship', on_delete=models.CASCADE, related_name='evaluations')

    attendance = models.PositiveSmallIntegerField(verbose_name="Devamlılık (1-10)")
    performance = models.PositiveSmallIntegerField(verbose_name="Performans (1-10)")
    adaptation = models.PositiveSmallIntegerField(verbose_name="Uyum (1-10)")
    technical_skills = models.PositiveSmallIntegerField(verbose_name="Teknik Yeterlilik (1-10)")
    communication_skills = models.PositiveSmallIntegerField(verbose_name="İletişim (1-10)")
    teamwork = models.PositiveSmallIntegerField(verbose_name="Takım Çalışması (1-10)")

    comment = models.TextField(verbose_name="Yorum", blank=True, null=True)
    average_rating = models.FloatField(verbose_name="Ortalama Puan", editable=False)
    is_approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.average_rating = round((
            self.attendance +
            self.performance +
            self.adaptation +
            self.technical_skills +
            self.communication_skills +
            self.teamwork
        ) / 6, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluation - {self.internship}"

    class Meta:
        verbose_name = "Değerlendirme"
        verbose_name_plural = "Değerlendirmeler"
