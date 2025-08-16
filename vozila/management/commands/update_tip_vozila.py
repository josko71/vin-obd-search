# vozila/management/commands/update_tip_vozila.py

from django.core.management.base import BaseCommand, CommandError
from vozila.models import CarModel, TipVozila

class Command(BaseCommand):
    help = 'Spremeni tip vozila za modele določenega imena.'

    def add_arguments(self, parser):
        parser.add_argument(
            'ime_modela',
            type=str,
            help='Ime modela, ki ga želite posodobiti.'
        )
        parser.add_argument(
            'novi_tip',
            type=str,
            help='Ime novega tipa vozila.'
        )

    def handle(self, *args, **options):
        # Odstranite morebitne presledke
        ime_modela = options['ime_modela'].strip()
        novi_tip_ime = options['novi_tip'].strip()

        self.stdout.write(f"Začetek posodabljanja modelov z imenom '{ime_modela}' na tip '{novi_tip_ime}'...")

        try:
            novi_tip_vozila = TipVozila.objects.get(ime__iexact=novi_tip_ime)
        except TipVozila.DoesNotExist:
            raise CommandError(f"Napaka: Tip vozila z imenom '{novi_tip_ime}' ne obstaja.")

        try:
            # KLJUČNA SPREMEMBA: Uporaba __icontains in ročnega preverjanja
            modeli_za_posodobitev = []
            
            # Najprej poiščite vse modele, ki vsebujejo iskani niz (manj strog filter)
            candidates = CarModel.objects.filter(ime__icontains=ime_modela)

            # Nato preverite vsakega kandidata
            for model in candidates:
                # Primerjajte niza po odstranitvi vseh presledkov in z velikimi tiskanimi črkami
                if model.ime.replace(' ', '').upper() == ime_modela.replace(' ', '').upper():
                    modeli_za_posodobitev.append(model.pk)

            if not modeli_za_posodobitev:
                self.stdout.write(self.style.WARNING(f"Opozorilo: V bazi niso bili najdeni nobeni modeli z imenom '{ime_modela}'."))
                return

            # Izvedite posodobitev
            updated_count = CarModel.objects.filter(pk__in=modeli_za_posodobitev).update(tip_vozila=novi_tip_vozila)
            
            self.stdout.write(self.style.SUCCESS(
                f'Uspešno posodobljenih {updated_count} modelov z imenom "{ime_modela}" na tip "{novi_tip_ime}".'
            ))

        except Exception as e:
            raise CommandError(f"Prišlo je do nepričakovane napake: {e}")