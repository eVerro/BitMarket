# -*- coding: UTF-8 -*-
from django.db import models
from BitMarket.index.models import UserProfile as User
from django.contrib import admin
from decimal import Decimal
import datetime


class UserProxy(User):
    """
    Klasa rozszerzająca klasę User
    rozszerza o metody tworzenia zleceń, kupowania zleceń
    i pobierania/depozytowania pieniędzy
    user - klucz obcy do tabeli UserData
    """

    def __unicode__(self):
        return '%s' % (self.user.name)

    class Meta:
        proxy = True

    def newCommission(self, source_amount, destination_amount, wallet_source, wallet_destination, dead_line):
        """
        @param String : source_amount
        @param String : destination_amount
        @param UserWallet : wallet_source
        @param UserWallet : wallet_destination
        @param datetime : dead_line
        tworzy nowe zlecenie, kwota source_amount będzie pobrana z portfelu wallet_source, a w razie
        kupna zlecenia przelewa kwote destination_amount na portfel wallet_destination
        wywołuje metody z wallet_destination: newPurchaseOffer(commission);    użycie metody jest zapisane w historii
        """
        # sprawdzenie danych wejściowych
        # czy portfele należą do osoby wywołującej funkcje
        if(wallet_source.user is not self):
            raise Exception('Portfel source jest przypisany do innego użytkownika.')
        if(wallet_destination.user is not self):
            raise Exception('Portfel destination jest przypisany do innego użytkownika.')
        # czy podane są właściwe
        if(Decimal(source_amount) < 0):
            raise Exception('source_amount jest poniżej zera.')
        if(Decimal(destination_amount) < 0):
            raise Exception('destination_amount jest poniżej zera.')
        if(Decimal(source_amount) > Decimal(wallet_source.account_balance)):
            raise Exception('source_amount jest powyżej stanu portfela.')
        if(dead_line - datetime.datetime.now()).total_seconds() < 0:
            raise Exception('Podana data jest z przeszłości.')
        commission = Commission(source_amount=source_amount, destination_amount=destination_amount, wallet_source=wallet_source, wallet_destination=wallet_destination, time_limit=dead_line)
        commission.save()
        wallet_source.newPurchaseOffer(commission)
        return 0

    def purchase(self, purchaser, purchased_commission):
        """
        @param Commission : purchased_commission
        zakup zlecenia
        wywołuje w odpowiednim portfelu metode purchase w portfelu użytkownika, który kupił
        oraz wywołuje sale w portfelu użytkownika, który sprzedał
        """
        # pobranie odpowiednich portfeli kupca
        purchaserwallet_source = UserWallet.objects.filter(user=purchaser, cryptocurrency=purchased_commission.destination_wallet.cryptocurrancy)
        purchaserwallet_destination = UserWallet.objects.filter(user=purchaser, cryptocurrency=purchased_commission.source_wallet.cryptocurrancy)
        # sprawdzenie poprawności portfeli
        if(not purchaserwallet_source):
            raise Exception("Nie istnieje odpowiedni portfel u kupca: %s" % (purchased_commission.destination_wallet.cryptocurrancy))
        if(not purchaserwallet_destination):
            raise Exception("Nie istnieje odpowiedni portfel u kupca: %s" % (purchased_commission.source_wallet.cryptocurrancy))
        # wywołanie metod do kupna i sprzedaży u kupującego
        purchaserwallet_destination.purchaseSell(purchased_commission)
        purchaserwallet_destination.purchase(purchased_commission)
        # wywołanie metody do sprzedaży u wystawiającego ofertę
        purchased_commission.wallet_source.sale(purchased_commission)

        return 0

    def withdraw(self, wallet, wallet_address, amount):
        """
        @param UserWallet : wallet
        @param String : wallet_address
        @param String : amount
        pobiera kwotę amount z konta i wysyłą ją na adres wallet_address
        zapisuje użycie metody w historii
        """
        wallet.withdraw(wallet_address=wallet_address,amount=amount)
        withdraw_history = DepositHistory(wallet_address=wallet_address,cryptocurrency=wallet.cryptocurrency,amount=amount,deposit=False)
        withdraw_history.save()
        return 0

    def deposit(self, wallet, wallet_address, amount):
        """
        @param UserWallet : wallet
        @param String : wallet_address
        @param String : amount
        zapisuje użycie metody w historii
        """
        wallet.deposit(wallet_address=wallet_address,amount=amount)
        deposit_history = DepositHistory(wallet_address=wallet_address,cryptocurrency=wallet.cryptocurrency,amount=amount,deposit=True)
        deposit_history.save()
        return 0


class Cryptocurrency(models.Model):
    """
    Klasa przechowująca nazwy możliwych do stworzenia portfeli
    """
    name = models.CharField(max_length="32", blank=False, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return '%s' % (self.name)


class Commission(models.Model):
    """
    Klasa reprezentująca zlecenie.
    Posiada pola takie jak:
    source_wallet - portfel fundujący zlecenie
    destination_wallet - portfel, na który zostanie przelana kwota po kupnie zlecenia
    source_amount - kwota pobrana już wcześniej z source_wallet
    destination_amount - kwota przelana po zrealizowaniu zlecenia na konto destination_wallet
    """
    source_wallet = models.ForeignKey("UserWallet", related_name='source_wallets')
    destination_wallet = models.ForeignKey("UserWallet", related_name='destination_wallets')
    source_amount = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    destination_amount = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    time_limit = models.DateTimeField()

    class Meta:
        ordering = []

    def __unicode__(self):
        return 'Z portfela %s na portfel %s' % (self.source_wallet, self.destination_wallet)


class History(models.Model):
    """
    User seller
    User purchaser
    Cryptocurrency cryptocurrency_sold
    Cryptocurrency cryptocurrency_bought
    int commission_id
    """
    seller = models.ForeignKey(User, related_name='sellers', unique=False)
    purchaser = models.ForeignKey(User, related_name='purchasers', unique=False, blank=True)
    cryptocurrency_sold = models.ForeignKey(Cryptocurrency, related_name='cryptocurrency_solds', unique=False, blank=False)
    cryptocurrency_bought = models.ForeignKey(Cryptocurrency, related_name='cryptocurrency_boughts', unique=False, blank=False)
    amount_sold = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    amount_bought = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    commission_id = models.IntegerField()


class CommissionHistory(models.Model):
    """
    Klasa histori działań użytkownika na giełdzie.
    Tz. tworzenie nowych zleceń, anulowanie, kupno.
    Pole action:
    0 - Stworzenie:
    1 - Kupno:
    2 - Sprzedanie:
    3 - Anulowanie:
    4 - Przeterminowane:
    Data executed_time
    int action
    """
    history = models.ForeignKey(History, unique=True)
    action = models.IntegerField()
    executed_time = models.DateTimeField()

    class Meta:
        ordering = []

    def __unicode__(self):
        return 'Historia zlecenia numer %d' % (self.history.commission_id)


class DepositHistory(models.Model):
    """
    Klasa histori przelewów użytkownika na giełdę, bądź z giełdy
    na zewnetrzne konta.
    Data executed_time
    Cryptocurrency cryptocurrency
    String wallet_address
    """
    wallet_address = models.CharField(max_length="64", blank=False, unique=False)
    cryptocurrency = models.ForeignKey(Cryptocurrency, unique=True)
    amount = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    executed_time = models.DateTimeField()
    deposit = models.BooleanField()


class UserWallet(models.Model):
    """
    Klasa podstawowa definiująca porfel użytkownika,
    rozszerzają jej możliwości proxy,
    ktore udostępniają metody do wpłaty i pobrania pieniędzy z portfela
    udostępiania metody do tworzenia zleceń, kupowania i pobierania pieniędzy
    """
    user = models.ForeignKey(User, unique=True)
    account_balance = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    cryptocurrency = models.ForeignKey(Cryptocurrency)
    commissions = models.ManyToManyField("Commission", related_name="commissions")
    
    def __unicode__(self):
        return '%s' % (self.cryptocurrency.name)

    def newPurchaseOffer(self, commission):
        """
        @param Commission : commission
        dodaje do bazy danych wpis o ofercie kupna,
        oraz odejmuje z konta potrzebną ilość gotówki,
        zapisuje użycie metody w historii
        """
        # sprawdzenie danych wejściowych
        # czy portfele należą do użytkownika, który wywołał funkcje
        if(commission.wallet_source.user is not self.user):
            raise Exception('Portfel source jest przypisany do innego użytkownika.')
        if(commission.wallet_destination.user is not self.user):
            raise Exception('Portfel destination jest przypisany do innego użytkownika.')
        # czy podane kwoty są poprawne
        if((commission.source_amount) < 0):
            raise Exception('source_amount jest poniżej zera.')
        if((commission.destination_amount) < 0):
            raise Exception('destination_amount jest poniżej zera.')
        if((commission.source_amount) > (self.account_balance)):
            raise Exception('source_amount jest powyżej stanu portfela.')
        # pobranie kwoty z konta
        self.account_balance = self.account_balance - commission.source_amount
        # zapis do bazy danych
        self.commissions.add(commission)
        self.full_clean(exclude=None, validate_unique=True)
        self.save()
        # dodanei wpisu do historii
        history = History(seller=self.user, commission=commission, cryptocurrency_sold=self.cryptocurrency, cryptocurrency_bought=commission.wallet_destination.cryptocurrency,
                           amount_sold=commission.source_amount, amount_bought=commission.destination_amount)
        history.save()
        purachse_history = CommissionHistory(history=history, action=0, executed_time=datetime.datetime.now())
        purachse_history.save()
        return 0

    def purchase(self, purchased_offer):
        """
        @param Commission : purchased_offer
        dodaje do konta kwotę z zatwierdzonej oferty
        zapisuje użycie metody w historii
        """
        if(purchased_offer.wallet_source.cryptocurrency is self.cryptocurrency):
            self.account_balance = (self.account_balance) + (purchased_offer.destination_amount) 
        else:
            raise Exception("Błąd w metodzie purchase")
        # pobranie histori
        history = History.objects.filter(commission_id=purchased_offer.id)
        # dodanei wpisu do historii
        purachse_history = CommissionHistory(history=history, action=1, executed_time=datetime.datetime.now())
        purachse_history.save()
        return 0

    def purchaseSell(self, purchased_offer):
        """
        @param Commission : purchased_offer
        odejmuje z konta kwotę z zatwierdzonej oferty
        """
        if(purchased_offer.wallet_destination.cryptocurrency is self.cryptocurrency):
            self.account_balance = (self.account_balance) - (purchased_offer.destination_amount) 
        else:
            raise Exception("Błąd w metodzie purchase")
        return 0

    def sale(self, saled_offer):
        """
        @param Commission : saled_offer
        dodaje do konta kwotę z sprzedanej oferty
        zapisuje użycie metody w historii
        """
        # zakladajacy zlecenie
        if(saled_offer.wallet_destination is self):
            self.account_balance = Decimal(self.account_balance) + Decimal(saled_offer.destination_amount)
        # przyjmujacy zlecenie
        elif(saled_offer.wallet_source.cryptocurrency is self.cryptocurrency):
            self.account_balance = Decimal(self.account_balance) + Decimal(saled_offer.source_amount)
        else:
            raise Exception("Błąd w metodzie sale")
        # pobranie histori i uaktualnienie wpisu
        history = History.objects.filter(commission_id=saled_offer.id)
        history.purchaser = self.user
        history.save()
        # dodanei wpisu do historii
        sale_history = CommissionHistory(history=history, action=2, executed_time=datetime.datetime.now())
        sale_history.save()
        return 0

#    class Meta:
#        """
#        @note: Ustawia klasę UserWallet jako klasa abstrakcyjna
#        """
#        abstract = True


class PLNWallet(UserWallet):
    """
    Klasa proxy UserWallet
    udostępiania metody do pobierania pieniędzy oraz składania depozytu
    na konta, które znajdują się poza serwerem
    Udostępnione metody działają na portfelach PLNC
    """

    def __unicode__(self):
        return '%s' % (self.cryptocurrency.name)

    class Meta:
        proxy = True

    def withdraw(self, amount, wallet_address):
        """
        @param Decimal : amount
        @param String : wallet_address
        pobiera kwotę amount z konta i wysyłą ją na adres wallet_address
        zapisuje użycie metody w historii
        """
        return 0

    def deposit(self, amount, wallet_address):
        """
        @param Decimal : amount
        @param String : wallet_address
        składanie depozytu o kwocie amount z konta wallet_address,
        WAŻNE : UZUPEŁNIĆ
        zapisuje użycie metody w historii
        """
        return 0


class LiteWallet(UserWallet):
    """
    Klasa proxy UserWallet
    udostępiania metody do pobierania pieniędzy oraz składania depozytu
    na konta, które znajdują się poza serwerem
    Udostępnione metody działają na portfelach LiteCoin
    """

    def __unicode__(self):
        return '%s' % (self.cryptocurrency.name)

    class Meta:
        proxy = True

    def withdraw(self, amount, wallet_address):
        """
        @param Decimal : amount
        @param String : wallet_address
        pobiera kwotę amount z konta i wysyłą ją na adres wallet_address
        zapisuje użycie metody w historii
        """
        return 0

    def deposit(self, amount, wallet_address):
        """
        @param Decimal : amount
        @param String : wallet_address
        WAŻNE : UZUPEŁNIĆ
        zapisuje użycie metody w historii
        """
        return 0


admin.site.register(User)
admin.site.register(Commission)
admin.site.register(History)
admin.site.register(CommissionHistory)
admin.site.register(DepositHistory)
admin.site.register(Cryptocurrency)
admin.site.register(LiteWallet)
admin.site.register(PLNWallet)
