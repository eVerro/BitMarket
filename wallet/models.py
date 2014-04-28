# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User


class UserWallet(models.Model):
    """
    Klasa abstrakcyjna definiująca porfel użytkownika
    udostępiania metody do tworzenia zleceń, kupowania i pobierania pieniędzy
    """
    user = models.ForeignKey(User, unique=True)
    account_balance = models.CharField(max_length="32", blank=False)

    def __unicode__(self):
        return self

    def newPurchaseOffer(self, commission):
        """
        @param Commission : commission
        dodaje do bazy danych wpis o ofercie kupna,
        oraz odejmuje z konta potrzebną ilość gotówki,
        w razie niewypału zwraca wyjątek commission.
        zapisuje użycie metody w historii
        """
        return 0

    def newSaleOffer(self, commission):
        """
        @param Commission : commission
        dodaje do bazy danych wpis o ofercie sprzedaży
        zapisuje użycie metody w historii
        """
        return 0

    def purchase(self, purchasedOffer):
        """
        @param Commission : purchasedOffer
        dodaje/odejmuje do/z konta kwotę z zatwierdzonej oferty
        zapisuje użycie metody w historii
        """
        return 0

    def sale(self, saledOffer):
        """
        @param Commission : saledOffer
        dodaje do konta kwotę z sprzedanej oferty
        zapisuje użycie metody w historii
        """
        return 0

    class Meta:
        """
        @note: Ustawia klasę UserWallet jako klasa abstrakcyjna
        zapisuje użycie metody w historii
        """
        abstract = True


class PLNWallet(UserWallet):
    """
    Klasa pochodna z UserWallet
    udostępiania metody do pobierania pieniędzy oraz składania depozytu
    na konta, które znajdują się poza serwerem
    Udostępnione metody działają na portfelach PLNC
    """
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
        Zapi
        """
        return 0


class LiteWallet(UserWallet):
    """
    Klasa pochodna z UserWallet
    udostępiania metody do pobierania pieniędzy oraz składania depozytu
    na konta, które znajdują się poza serwerem
    Udostępnione metody działają na portfelach LiteCoin
    """
    def withdraw(self, amount, walletAddress):
        """
        @param String : amount
        @param String : walletAddress
        pobiera kwotę amount z konta i wysyłą ją na adres walletAddress
        """
        return 0

    def deposit(self, amount, walletAddress):
        """
        @param String : amount
        @param String : walletAddress
        """
        return 0
