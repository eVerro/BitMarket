# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User as UserData
from django.contrib import admin
from decimal import Decimal
import datetime


class User(UserData):
    """
    Klasa rozszerzająca klasę User
    rozszerza o metody tworzenia zleceń, kupowania zleceń 
    i pobierania/depozytowania pieniędzy
    """
    user = models.ForeignKey(UserData, unique=True, related_name="users")

    def __unicode__(self):
        return '%s' % (self.user.name)

    class Meta:
        ordering = []

    def newCommission(self, sourceAmount, destinationAmount, walletSource, walletDestination):
        """
        @param String : sourceAmount
        @param String : destinationAmount
        @param UserWallet : walletSource
        @param UserWallet : walletDestination
        tworzy nowe zlecenie, kwota sourceAmount będzie pobrana z portfelu walletSource, a w razie
        kupna zlecenia przelewa kwote destinationAmount na portfel walletDestination
        wywołuje metody z walletSource:  newSaleOffer(commission);    użycie metody jest zapisane w historii
        wywołuje metody z walletDestination: newPurchaseOffer(commission);    użycie metody jest zapisane w historii
        """
        # sprawdzenie danych wejściowych
        # czy portfele należą do osoby wywołującej funkcje
        if(walletSource.user is not self):
            raise Exception('Portfel source jest przypisany do innego użytkownika.')
        if(walletDestination.user is not self):
            raise Exception('Portfel destination jest przypisany do innego użytkownika.')
        # czy podane są właściwe
        if(Decimal(sourceAmount) < 0):
            raise Exception('sourceAmount jest poniżej zera.')
        if(Decimal(destinationAmount) < 0):
            raise Exception('destinationAmount jest poniżej zera.')
        if(Decimal(sourceAmount) > Decimal(walletSource.account_balance)):
            raise Exception('sourceAmount jest powyżej stanu portfela.')
        commission = Commission(sourceAmount=sourceAmount, destinationAmount=destinationAmount, walletSource=walletSource, walletDestination=walletDestination)
        commission.save()
        walletSource.newPurchaseOffer(commission)
        walletDestination.newSaleOffer(commission)
        # zapisanie do bazy danych
        walletSource.save()
        walletDestination.save()
        return 0

    def purchase(self, purchaser, purchasedCommission):
        """
        @param Commission : purchasedCommission
        zakup zlecenia
        wywołuje w odpowiednim portfelu metode purchase i sale w portfelu użytkownika, który kupił
        oraz wywołuje sale w portfelu użytkownika, który sprzedał
        """
        # pobranie odpowiednich portfeli kupca
        purchaserWalletSource = UserWallet.objects.filter(user=purchaser, cryptocurrency=purchasedCommission.destinationWallet.cryptocurrancy)
        purchaserWalletDestination = UserWallet.objects.filter(user=purchaser, cryptocurrency=purchasedCommission.sourceWallet.cryptocurrancy)
        # sprawdzenie poprawności portfeli
        if(not purchaserWalletSource):
            raise Exception("Nie istnieje odpowiedni portfel u kupca: %s" % (purchasedCommission.destinationWallet.cryptocurrancy))
        if(not purchaserWalletDestination):
            raise Exception("Nie istnieje odpowiedni portfel u kupca: %s" % (purchasedCommission.sourceWallet.cryptocurrancy))
        # wywołanie metod do kupna i sprzedaży u kupującego
        purchaserWalletDestination.purchase(purchasedCommission)
        # wywołanie metody do sprzedaży u wystawiającego ofertę
        purchasedCommission.walletSource.purchase(purchasedCommission)
        purchasedCommission.walletSource.sale(purchasedCommission)
        
        return 0

    def withdraw(self, walletSource, walletAddress, amount):
        """
        @param UserWallet : walletSource
        @param String : walletAddress
        @param String : amount
        pobiera kwotę amount z konta i wysyłą ją na adres walletAddress
        zapisuje użycie metody w historii
        """
        return 0

    def deposit(self, walletSource, walletAddress, amount):
        """
        @param UserWallet : walletSource
        @param String : walletAddress
        @param String : amount
        WAŻNE : UZUPEŁNIĆ
        zapisuje użycie metody w historii
        """
        return 0


class Commission(models.Model):
    """
    Klasa reprezentująca zlecenie.
    Posiada pola takie jak:
    sourceWallet - portfel fundujący zlecenie
    destinationWallet - portfel, na który zostanie przelana kwota po kupnie zlecenia
    sourceAmount - kwota pobrana już wcześniej z sourceWallet
    destinationAmount - kwota przelana po zrealizowaniu zlecenia na konto destinationWallet 
    """
    sourceWallet = models.ForeignKey("UserWallet", related_name='sourceWallets')
    destinationWallet = models.ForeignKey("UserWallet", related_name='destinationWallets')
    sourceAmount = models.CharField(max_length="32", blank=False)
    destinationAmount = models.CharField(max_length="32", blank=False)

    class Meta:
        ordering = []

    def __unicode__(self):
        return 'Z portfela %s na portfel %s' % (self.sourceWallet, self.destinationWallet)


class History(models.Model):
    """
    Klasa reprezentująca historię zleceń portfeli.
    Zapisywane są w niej wszystkie operacje UserWallet
    Tz. newPurchaseOffer, newSaleOffer, purchase, sale
    """
    function = models.CharField(max_length="32", blank=False)
    commission = models.ForeignKey("Commission")
    executedTime = models.DateTimeField()

    class Meta:
        ordering = []

    def __unicode__(self):
        return 'Zrobionop %s. Powiązane z zleceniem %s. Data: %s' % (self.function, self.commission, self.executedTime)


class Cryptocurrency(models.Model):
    """
    Klasa przechowująca nazwy możliwych do stworzenia portfeli
    """
    name = models.CharField(max_length="32", blank=False, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return '%s' % (self.name)


class UserWallet(models.Model):
    """
    Klasa podstawowa definiująca porfel użytkownika,
    rozszerzają jej możliwości proxy,
    ktore udostępniają metody do wpłaty i pobrania pieniędzy z portfela
    udostępiania metody do tworzenia zleceń, kupowania i pobierania pieniędzy
    """
    user = models.ForeignKey(User, unique=True)
    account_balance = models.CharField(max_length="32", blank=False)
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
        if(commission.walletSource.user is not self.user):
            raise Exception('Portfel source jest przypisany do innego użytkownika.')
        if(commission.walletDestination.user is not self.user):
            raise Exception('Portfel destination jest przypisany do innego użytkownika.')
        # czy podane kwoty są poprawne
        if(Decimal(commission.sourceAmount) < 0):
            raise Exception('sourceAmount jest poniżej zera.')
        if(Decimal(commission.destinationAmount) < 0):
            raise Exception('destinationAmount jest poniżej zera.')
        if(Decimal(commission.sourceAmount) > Decimal(self.account_balance)):
            raise Exception('sourceAmount jest powyżej stanu portfela.')
        self.account_balance = Decimal(self.account_balance) - Decimal(commission.sourceAmount)
        self.account_balance = "" + self.account_balance
        self.commissions.add(commission)
        self.full_clean(exclude=None, validate_unique=True)
        # dodanei wpisu do historii
        historyOffer = History(function="newPurchaseOffer", commission=commission, executedTime=datetime.datetime.now())
        historyOffer.save()
        return 0

    def newSaleOffer(self, commission):
        """
        @param Commission : commission
        dodaje do bazy danych wpis o ofercie sprzedaży
        zapisuje użycie metody w historii
        """
        if(commission.walletSource.user is not self.user):
            raise Exception('Portfel source jest przypisany do innego użytkownika.')
        if(commission.walletDestination.user is not self.user):
            raise Exception('Portfel destination jest przypisany do innego użytkownika.')
        if(commission.sourceAmount < 0):
            raise Exception('sourceAmount jest poniżej zera.')
        if(commission.destinationAmount < 0):
            raise Exception('destinationAmount jest poniżej zera.')
        self.commissions.add(commission)
        # dodanei wpisu do historii
        historyOffer = History(function="newPurchaseOffer", commission=commission, executedTime=datetime.datetime.now())
        historyOffer.save()
        return 0

    def purchase(self, purchasedOffer):
        """
        @param Commission : purchasedOffer
        dodaje/odejmuje do/z konta kwotę z zatwierdzonej oferty
        zapisuje użycie metody w historii
        """
        if(purchasedOffer.walletDestination.cryptocurrency is self.cryptocurrency):
            self.account_balance = Decimal(self.account_balance) - Decimal(purchasedOffer.destinationAmount)
        else:
            raise Exception("Błąd w metodzie purchase")
        # dodanei wpisu do historii
        historyOffer = History(function="newPurchaseOffer", commission=purchasedOffer, executedTime=datetime.datetime.now())
        historyOffer.save()
        return 0

    def sale(self, saledOffer):
        """
        @param Commission : saledOffer
        dodaje do konta kwotę z sprzedanej oferty
        zapisuje użycie metody w historii
        """
        # zakladajacy zlecenie
        if(saledOffer.walletDestination is self):
            self.account_balance = Decimal(self.account_balance) + Decimal(saledOffer.destinationAmount)
        # przyjmujacy zlecenie
        elif(saledOffer.walletSource.cryptocurrency is self.cryptocurrency):
            self.account_balance = Decimal(self.account_balance) + Decimal(saledOffer.sourceAmount)
        else:
            raise Exception("Błąd w metodzie sale")
        # dodanei wpisu do historii
        historyOffer = History(function="newPurchaseOffer", commission=saledOffer, executedTime=datetime.datetime.now())
        historyOffer.save()
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

    def withdraw(self, amount, walletAddress):
        """
        @param String : amount
        @param String : walletAddress
        pobiera kwotę amount z konta i wysyłą ją na adres walletAddress
        zapisuje użycie metody w historii
        """
        return 0

    def deposit(self, amount, walletAddress):
        """
        @param String : amount
        @param String : walletAddress
        składanie depozytu o kwocie amount z konta walletAddress,
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

    def withdraw(self, amount, walletAddress):
        """
        @param String : amount
        @param String : walletAddress
        pobiera kwotę amount z konta i wysyłą ją na adres walletAddress
        zapisuje użycie metody w historii
        """
        return 0

    def deposit(self, amount, walletAddress):
        """
        @param String : amount
        @param String : walletAddress
        WAŻNE : UZUPEŁNIĆ
        zapisuje użycie metody w historii
        """
        return 0


admin.site.register(User)
admin.site.register(Commission)
admin.site.register(History)
admin.site.register(Cryptocurrency)
admin.site.register(LiteWallet)
admin.site.register(PLNWallet)

