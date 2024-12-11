from django.db import models

# Create your models here.
class Parameter_Settings(models.Model):
    sr_no = models.CharField(max_length=10)
    part_model = models.CharField(max_length=100)
    part_name = models.CharField(max_length=100)
    char_lock = models.CharField(max_length=100)
    char_lock_limit = models.CharField(max_length=100)
    punch_no = models.BooleanField(default=False)

    def __str__(self):
        return f"ParameterSettings for {self.part_model}"

class paraTableData(models.Model):
    parameter_settings = models.ForeignKey(Parameter_Settings, related_name='table_data', on_delete=models.CASCADE)
    sr_no = models.CharField(max_length=10)
    parameter_name = models.CharField(max_length=100, blank=True)
    channel_no = models.CharField(max_length=10, blank=True)
    low_master = models.CharField(max_length=100, blank=True)
    high_master = models.CharField(max_length=100, blank=True)
    nominal = models.CharField(max_length=100, blank=True)
    lsl = models.CharField(max_length=100, blank=True)
    usl = models.CharField(max_length=100, blank=True)
    ltl = models.CharField(max_length=100, blank=True)
    utl = models.CharField(max_length=100, blank=True)
    step_no = models.CharField(max_length=10, blank=True)
    auto_man = models.BooleanField(default=False)
    timer = models.CharField(max_length=100, blank=True)
    digits = models.CharField(max_length=10, blank=True)
    id_od = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"TableData for {self.parameter_name} ({self.sr_no})"
    

class Operator_setting(models.Model):
    operator_no = models.CharField(max_length=10)
    operator_name = models.CharField(max_length=100)


class master_data(models.Model):
    a = models.FloatField()
    a1 = models.IntegerField()
    b = models.FloatField()
    b1 = models.IntegerField()
    e = models.CharField(max_length=10)
    d = models.FloatField()
    o1 = models.FloatField()
    parameter_name = models.CharField(max_length=100)
    part_model = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    mastering = models.CharField(max_length=10)
    probe_number = models.IntegerField()  # Add probeNumber as a field


    def __str__(self):
        return f"{self.parameter_name} - {self.part_model}"