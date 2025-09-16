from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Movie, Review

class MovieAdminForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If amount_left is 0, make the field read-only
        if self.instance and self.instance.amount_left == 0:
            self.fields['amount_left'].disabled = True
            self.fields['amount_left'].help_text = "Cannot modify amount_left when it's 0. Create a new movie instead."
    
    def clean_amount_left(self):
        amount_left = self.cleaned_data.get('amount_left')
        
        # If this is an existing instance and amount_left was 0
        if self.instance and self.instance.amount_left == 0:
            # Don't allow changing from 0
            if amount_left != 0:
                raise ValidationError("Cannot change amount_left from 0. Create a new movie instead.")
        
        # Always validate that amount_left is not negative
        if amount_left is not None and amount_left < 0:
            raise ValidationError("Amount left cannot be negative.")
            
        return amount_left

class MovieAdmin(admin.ModelAdmin):
    form = MovieAdminForm
    list_display = ('name', 'price', 'amount_left', 'is_available')
    list_filter = ('amount_left',)
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'description', 'image')
        }),
        ('Inventory', {
            'fields': ('amount_left',),
            'description': 'Set to 0 to hide from public listings.'
        }),
    )
    
    def is_available(self, obj):
        return obj.amount_left > 0
    is_available.boolean = True
    is_available.short_description = 'Available'

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)