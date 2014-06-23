# -*- coding: UTF-8 -*-
from BitMarket.index.models import UserProfile as User
from BitMarket.index.smsapi import Smsapi
from decimal import Decimal
from django.contrib import admin
from django.db import models
from django.utils.timezone import utc
import datetime
import hashlib
import random
import sys
import wallet
from django.contrib.auth.hashers import check_password



class UserProxy(User):
    """
    Proxy usera, posiada metody tworzenia zleceń, kupowania zleceń
    i pobierania/depozytowania pieniędzy
    """

    def __unicode__(self):
        return 'Użytkownik %s' % (self.username)

    """
    Podczas tworzenia nowego użytkownika są tworzone od razu dla niego nowe portfele.
    """
        
    def save(self):
        super(UserProxy, self).save()
        cryptocurrency = Cryptocurrency.objects.all()
        for c in cryptocurrency:
            wallet = UserWallet(user=self,account_balance=0,cryptocurrency=c, code=1)
            wallet.save()
            
    class Meta:
        proxy = True

    def newCommission(self, source_amount, destination_amount, source_wallet, destination_wallet, dead_line):
        """
        @param String : source_amount kwota pobierana z konta użytkownika
        @param String : destination_amount kwota, którą dostanie użytkownik w razie wykonania transakcji
        @param UserWallet : source_walllet portfel, z kótrego będzie pobierana kwota source_amount 
        @param UserWallet : destination_wallet portfel, na który trafią pieniądze z destination_amount
        @param datetime : dead_line, czas, po którym zlecenie zostanie ustawione na overdue
        @param decimal : provision procent prowizji pobierany od transakcji
        @param bool : source_provision, jezeli sell jest true to prowizja jest pobierana przy tworzeniu transakcji od kwoty source_amount z portfela source_wallet,
        w przypadku false kwota sprzedaży po prostu zostanie zwiększona.
        
        tworzy nowe zlecenie, kwota source_amount będzie pobrana z portfelu source_wallet, a w razie
        kupna zlecenia przelewa kwote destination_amount na portfel destination_wallet
        wywołuje metody z destination_wallet: newPurchaseOffer(commission);    użycie metody jest zapisane w historii
        """
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        source_amount = Decimal(str(source_amount))
        destination_amount = Decimal(str(destination_amount))
        # sprawdzenie danych wejściowych
        # czy portfele należą do osoby wywołującej funkcje
        
        if(self.id is not source_wallet.user.id):
            raise Exception('Portfel source jest przypisany do innego użytkownika.')
        if(self.id is not destination_wallet.user.id):
            raise Exception('Portfel destination jest przypisany do innego użytkownika.')
        # czy podane są właściwe
        if(Decimal(source_amount) < 0):
            raise Exception('source_amount jest poniżej zera.')
        if(Decimal(destination_amount) < 0):
            raise Exception('destination_amount jest poniżej zera.')
        if(Decimal(source_amount) > Decimal(source_wallet.account_balance)):
            raise Exception('Masz za mało kasy. Posiadasz %s, a chcesz zlecenie za %s dupku' % (Decimal(source_wallet.account_balance), Decimal(source_amount)))
        if((dead_line - now).total_seconds()) < 0:
            raise Exception('Podana data jest z przeszłości.')
        commission = Commission(source_amount=source_amount, destination_amount=destination_amount, source_wallet=source_wallet, destination_wallet=destination_wallet, time_limit=dead_line)
        commission.save()
        AdminWallets.addProvisionToCommission(commission)
        source_wallet.newPurchaseOffer(commission)
        return 0

    def purchase(self, purchased_commission):
        """
        @param Commission : purchased_commission
        zakup zlecenia
        wywołuje w odpowiednim portfelu metode purchase w portfelu użytkownika, który kupił
        oraz wywołuje sale w portfelu użytkownika, który sprzedał
        """
        # pobranie odpowiednich portfeli kupca
        purchasersource_walllet = UserWallet.objects.filter(user=self.id, cryptocurrency=purchased_commission.destination_wallet.cryptocurrency)
        purchaserdestination_wallet = UserWallet.objects.filter(user=self.id, cryptocurrency=purchased_commission.source_wallet.cryptocurrency)
        # sprawdzenie poprawności portfeli
        
        if(not purchasersource_walllet):
            raise Exception("Nie istnieje odpowiedni portfel u kupca: %s" % (purchased_commission.destination_wallet.cryptocurrency))
        if(not purchaserdestination_wallet):
            raise Exception("Nie istnieje odpowiedni portfel u kupca: %s" % (purchased_commission.source_wallet.cryptocurrency))
        # wywołanie metod do kupna i sprzedaży u kupującego
        
        
        purchasersource_walllet[0].purchaseSell(purchased_commission)
        purchasersource_walllet[0].save()
        
        AdminWallets.takeProvision(purchased_commission)
        
        purchaserdestination_wallet[0].purchase(purchased_commission)
        purchaserdestination_wallet[0].save()
        
        # wywołanie metody do sprzedaży u wystawiającego ofertę
        
        purchased_commission.destination_wallet.sale(purchased_commission)
        purchased_commission.destination_wallet.save()
        
        purchased_commission.delete()
        
        return 0
    
    def cancelCommission(self, commission):
        """
        Anuluje zlecenie.
        """
        if(self.id is not commission.source_wallet.user.id):
            raise Exception('Użytkownik próbuje anulować nieswoje zlecenie.')
        if(self.id is not commission.destination_wallet.user.id):
            raise Exception('Użytkownik próbuje anulować nieswoje zlecenie.')
        
        commission.source_wallet.account_balance = UserWallet.objects.filter(user=self, cryptocurrency=commission.source_wallet.cryptocurrency)[0].account_balance
        commission.source_wallet.account_balance = commission.source_wallet.account_balance + commission.source_amount
        commission.source_wallet.save()
        
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        
        # pobranie histori i uaktualnienie wpisu
        history = History.objects.filter(commission_id=commission.id)
        history = history[0]
        history.commission_id=None
        history.executed_time=now
        history.save()
        
        commission.delete()
        
    def getBoughtHistory(self, cryptocurrency_sold, cryptocurrency_bought, sort=None):
        """
        Zwraca tylko zlecenia zrealizowano, gdzie wymieniono cryptocurrency_sold na cryptocurrency_bought.
        można sortować po:
        amount_sold
        amount_bought
        sold_price - amount_sold/amount_bought
        bought_price - amount_bought/amount_sold
        executed_time
        """
        if(not hasattr(cryptocurrency_sold, 'id')):
            cryptocurrency_sold = Cryptocurrency.objects.filter(name=cryptocurrency_sold)[0]
        if(not hasattr(cryptocurrency_bought, 'id')):
            cryptocurrency_bought = Cryptocurrency.objects.filter(name=cryptocurrency_bought)[0]
        if(sort==None):
            return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s) and cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s'], params=[self.id, self.id, cryptocurrency_sold.id, cryptocurrency_bought.id])
        return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s) and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[self.id, self.id, cryptocurrency_sold.id, cryptocurrency_bought.id, cryptocurrency_sold.id,cryptocurrency_bought.id], order_by=[sort])
    
    def getExchangeHistory(self, cryptocurrency_first=None, cryptocurrency_second=None, sort=None):
        """
        Zwraca tylko zrealizowane.
        można sortować po:
        amount_sold
        amount_bought
        create_time
        sold_price - amount_sold/amount_bought
        bought_price - amount_bought/amount_sold
        executed_time
        """
        if(cryptocurrency_first==None):
            if(sort==None):
                return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s)'], 
                                     params=[self.id, self.id])
            return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s)'], 
                                 params=[self.id, self.id], order_by=[sort])
        if(not hasattr(cryptocurrency_first, 'id')):
            cryptocurrency_first = Cryptocurrency.objects.filter(name=cryptocurrency_first)[0]
        if(cryptocurrency_second==None):
            if(sort==None):
                return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s) and (cryptocurrency_sold_id=%s or cryptocurrency_bought_id=%s)'], 
                                     params=[self.id, self.id, cryptocurrency_first.id])
            return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s) and (cryptocurrency_sold_id=%s or cryptocurrency_bought_id=%s)'], 
                                 params=[self.id, self.id, cryptocurrency_first.id, cryptocurrency_first.id], order_by=[sort])
        if(not hasattr(cryptocurrency_second, 'id')):
            cryptocurrency_second = Cryptocurrency.objects.filter(name=cryptocurrency_second)[0]
        if(sort==None):
            return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s) and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[self.id, self.id, cryptocurrency_first.id, cryptocurrency_second.id, cryptocurrency_first.id,cryptocurrency_second.id])
        return History.objects.extra(where=['purchaser_id is not null and (purchaser_id is %s or seller_id is %s) and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[self.id, self.id, cryptocurrency_first.id, cryptocurrency_second.id, cryptocurrency_first.id,cryptocurrency_second.id], order_by=[sort])
        
    def getCommissionHistoryTwoWallets(self, cryptocurrency_first, cryptocurrency_second, sort=None):
        """
        Zwraca wszystkie zlecenia: anulowane, przeterminowane, wystawione, kupione i sprzedane użytkownika z dwóch walut 
        można sortować po:
        amount_sold
        amount_bought
        create_time
        sold_price - amount_sold/amount_bought
        bought_price - amount_bought/amount_sold
        """
        if(sort==None):
            return History.objects.extra(where=['(purchaser_id is %s or seller_id is %s) and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[cryptocurrency_first.id, cryptocurrency_second.id, cryptocurrency_first.id,cryptocurrency_second.id])
        return History.objects.extra(where=['(purchaser_id is %s or seller_id is %s) and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[cryptocurrency_first.id, cryptocurrency_second.id, cryptocurrency_first.id,cryptocurrency_second.id], order_by=[sort])
    
    def getCommissionHistory(self, sort=None):
        """
        Zwraca wszystkie zlecenia: anulowane, przeterminowane, wystawione, kupione i sprzedane użytkownika
        można sortować po:
        amount_sold
        amount_bought
        create_time
        sold_price - amount_sold/amount_bought
        bought_price - amount_bought/amount_sold
        """
        if(sort==None):
            return History.objects.extra(where=['(purchaser_id is %s or seller_id is %s)'], params=[self.id, self.id])
        return History.objects.extra(where=['(purchaser_id is %s or seller_id is %s)'], params=[self.id, self.id], order_by=[sort])
        
    
    def getCommissions(self, sort=None):
        """
        W parametrach można podać nazwy albo obiekty Cryptocurrency
        można sortować po:
        source_wallet
        destination_wallet 
        source_amount 
        destination_amount 
        time_limit
        source_price
        destination_price 
        """
        if(sort==None):
            return Commission.objects.extra(where=["(source_wallet_id in (Select id from wallet_userwallet where user_id == %s))"], 
                                            params=[self.id])
        return Commission.objects.extra(where=["(source_wallet_id in (Select id from wallet_userwallet where user_id == %s))"], 
                                            params=[self.id], order_by=[sort])
        
    def withdraw(self, wallet, wallet_address=None, amount=None):
        """
        @param UserWallet : wallet
        @param String : wallet_address
        @param String : amount
        pobiera kwotę amount z konta i wysyłą ją na adres wallet_address
        """
        amount=Decimal(str(amount))
        wallet.withdrawRequest()
        wallet.save()
        return 0

    def deposit(self, wallet, wallet_address, amount):
        """
        @param UserWallet : wallet
        @param String : wallet_address
        @param String : amount
        """
        amount=Decimal(str(amount))
        wallet.deposit(wallet_address=wallet_address,amount=amount)
        wallet.save()
        return 0
    
    def getDepositSum(self, wallet):
        if(not hasattr(wallet, 'id')):
            wallet = UserWallet.objects.filter(id=wallet)[0]
        history = DepositHistory.objects.filter(user=self, cryptocurrency=wallet.cryptocurrency, deposit=True)
        amount = 0
        for his in history:
            amount = amount + his.amount
        return amount
    
    def getWithdrawSum(self, wallet):
        if(not hasattr(wallet, 'id')):
            wallet = UserWallet.objects.filter(id=wallet)[0]
        history = DepositHistory.objects.filter(user=self, cryptocurrency=wallet.cryptocurrency, deposit=False)
        amount = 0
        for his in history:
            amount = amount + his.amount
        return amount
    
    def changePassword(self, old_password, new_password):
        user = User.objects.filter(id=self.id)[0]
        if(not check_password(old_password, user.password)):
            raise Exception("Podałeś złe hasło")
        hashs = hashlib.md5()
        hashs.update(new_password)
        new_password = hashs.hexdigest()
        user.password = new_password
        user.save()
        return 0
    
    def changeMail(self, old_mail, new_mail):
        if(self.email != old_mail):
            raise Exception("Podałeś złe hasło")
        user = User.objects.filter(id=self.id)[0]
        user.email = new_mail
        user.save()
        return 0
            
            
        
class Cryptocurrency(models.Model):
    """
    Klasa przechowująca nazwy możliwych do stworzenia portfeli
    """
    name = models.CharField(max_length="32", blank=False, unique=True)
    
    """
    Inicjalizacja nowej waluty polega na tym, że każdemu użytkownikowi jest tworzony portfel z tą własnie nową walutą.
    """
        
    def save(self):
        super(Cryptocurrency, self).save()
        users = User.objects.all()
        for user in users:
            wallet = UserWallet(user=user,account_balance=0,cryptocurrency=self)
            wallet.save()
            
    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return 'Kryptowaluta %s' % (self.name)


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
    source_price = models.DecimalField(max_digits=64, decimal_places=32, blank=True,null=False)
    destination_price = models.DecimalField(max_digits=64, decimal_places=32, blank=True,null=False)
    
    
    def save(self):
        self.source_price = Decimal(Decimal(self.source_amount)/Decimal(self.destination_amount))
        self.destination_price = Decimal(Decimal(self.destination_amount)/Decimal(self.source_amount))
        super(Commission, self).save()

    class Meta:
        ordering = []

    def __unicode__(self):
        return 'Wymiana z %s %s na %s %s %s' % (self.source_amount, self.source_wallet.cryptocurrency.name, self.destination_amount, self.destination_wallet.cryptocurrency.name, self.source_wallet.user.username)
    
    def overdue(self):
        # pobranie histori i uaktualnienie wpisu
        history = History.objects.filter(commission_id=self.id)
        history = history[0]
        history.commission_id=None
        history.save()
        self.source_wallet.account_balance = Decimal(UserWallet.objects.filter(id = self.source_wallet.id)[0].account_balance) + Decimal(self.source_amount)
        self.source_wallet.save()
        self.delete()
        
    @staticmethod
    def getCommissions(cryptocurrency_sold, cryptocurrency_bought, sort=None):
        """
        W parametrach można podać nazwy albo obiekty Cryptocurrency
        można sortować po:
        source_wallet
        destination_wallet 
        source_amount 
        destination_amount 
        time_limit
        source_price
        destination_price 
        """
        print cryptocurrency_sold
        print cryptocurrency_bought
        if(not hasattr(cryptocurrency_sold, 'id')):
            cryptocurrency_sold = Cryptocurrency.objects.filter(name=cryptocurrency_sold)[0]
        if(not hasattr(cryptocurrency_bought, 'id')):
            cryptocurrency_bought = Cryptocurrency.objects.filter(name=cryptocurrency_bought)[0]
        
        if(sort==None):
            return Commission.objects.extra(where=["((source_wallet_id in (Select id from wallet_userwallet where cryptocurrency_id == %s)) AND (destination_wallet_id in (Select id from wallet_userwallet where cryptocurrency_id == %s)))"], 
                                            params=[cryptocurrency_sold.id,cryptocurrency_bought.id])
        return Commission.objects.extra(where=["((source_wallet_id in (Select id from wallet_userwallet where cryptocurrency_id == %s)) AND (destination_wallet_id in (Select id from wallet_userwallet where cryptocurrency_id == %s)))"], 
                                        params=[cryptocurrency_sold.id,cryptocurrency_bought.id], order_by=[sort])
        
        
class History(models.Model):
    """
    Historia zlecenia.
    seller wymienia się kryptowalute cryptocurrency_sold na cryptocurrency_bought z purchaser.
    
    W przypadku gdy purchaser jest równy None to oznacza, że waluta nie została sprzedana, czyli zlecenie może być anulowane, przeterminowane bądź jeszcze niezrealizowane.
    W przypadku gdy commission_id jest równy None to onzacza, że zlecenie zostało zakończone, czyli mogło być kupione, anulowane, przeterminowane.
    W przypadku gdy executed_time jest równy None to onzacza, że zlecenie nie zostało kupione ani anulowane, czyli mogło być przeterminowane bądź jeszcze niezrealizowane.
    
    Gdy jest kupione/sprzedane to purchaser wskazuje na kupca, commission_id = None, executed_time wkazuje kiedy zostało zrealizowane kupno.
    Gdy jest niezrealizowane jeszcze to purchaser = None, commission_id wskazuje na id zlecenia, do którego jest podpięta historia i executed_time = None.
    Gdy jest anulowane to purchaser = None, commission_id = None i executed_time wkazuje kiedy anulowanio.
    Gdy jest przeterminowane to purchaser = None, commission_id = None i executed_time = None.
    
    seller - sprzedawca.
    purchaser - kupujący.
    cryptocurrency_sold - seller sprzedaje tą walute.
    cryptocurrency_bought - purchaser sprzedaje tą walutę, inaczej seller kupuje ją.
    amount_sold - kwota sprzedawana.
    amount_bought - kwota kupowana.
    commission_id - w przypadku istnienia zlecenia, jest tutaj id tego zlecenia.
    create_time - data stworzenia zlecenia.
    executed_time - data sprzedania, anulowania zlecenia.
    """
    seller = models.ForeignKey(User, related_name='sellers', unique=False, blank=False)
    purchaser = models.ForeignKey(User, related_name='purchasers', unique=False, blank=True, null=True)
    cryptocurrency_sold = models.ForeignKey(Cryptocurrency, related_name='cryptocurrency_solds', unique=False, blank=False)
    cryptocurrency_bought = models.ForeignKey(Cryptocurrency, related_name='cryptocurrency_boughts', unique=False, blank=False)
    amount_sold = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    amount_bought = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    commission_id = models.IntegerField(unique=True, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True)
    executed_time = models.DateTimeField(blank=True,null=True)
    sold_price = models.DecimalField(max_digits=64, decimal_places=32, blank=True,null=False)
    bought_price = models.DecimalField(max_digits=64, decimal_places=32, blank=True,null=False)
    
    def save(self):
        self.sold_price = Decimal(Decimal(self.amount_sold)/Decimal(self.amount_bought))
        self.bought_price = Decimal(Decimal(self.amount_bought)/Decimal(self.amount_sold))
        super(History, self).save()
                                
    @staticmethod
    def getBoughtHistory(cryptocurrency_sold, cryptocurrency_bought, sort=None):
        """
        amount_sold
        amount_bought
        sold_price - amount_sold/amount_bought
        bought_price - amount_bought/amount_sold
        """
        if(not hasattr(cryptocurrency_sold, 'id')):
            cryptocurrency_sold = Cryptocurrency.objects.filter(name=cryptocurrency_sold)[0]
        if(not hasattr(cryptocurrency_bought, 'id')):
            cryptocurrency_bought = Cryptocurrency.objects.filter(name=cryptocurrency_bought)[0]
        if(sort==None):
            return History.objects.extra(where=['purchaser_id is not NULL', 'cryptocurrency_sold_id=%s','cryptocurrency_bought_id=%s'], params=[cryptocurrency_sold.id, cryptocurrency_bought.id])
        return History.objects.extra(where=['purchaser_id is not null and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[cryptocurrency_sold.id, cryptocurrency_bought.id, cryptocurrency_sold.id,cryptocurrency_bought.id], order_by=[sort])

    @staticmethod
    def getExchangeHistory(cryptocurrency_first, cryptocurrency_second, sort=None):
        """
        amount_sold
        amount_bought
        create_time
        amount_sold/amount_bought
        amount_bought/amount_sold
        """
        if(not hasattr(cryptocurrency_second, 'id')):
            cryptocurrency_second = Cryptocurrency.objects.filter(name=cryptocurrency_second)[0]
        if(not hasattr(cryptocurrency_first, 'id')):
            cryptocurrency_first = Cryptocurrency.objects.filter(name=cryptocurrency_first)[0]
        if(sort==None):
            return History.objects.extra(where=['purchaser_id is not null and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[cryptocurrency_first.id, cryptocurrency_second.id, cryptocurrency_second.id, cryptocurrency_first.id])
        return History.objects.extra(where=['purchaser_id is not null and ((cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s ) OR (cryptocurrency_sold_id=%s and cryptocurrency_bought_id=%s))'], 
                                     params=[cryptocurrency_first.id, cryptocurrency_second.id, cryptocurrency_second.id, cryptocurrency_first.id], order_by=[sort])
    
    def __unicode__(self):
        if(self.purchaser is None):
            if(self.commission_id is None):
                if(self.executed_time is None):
                    return 'Historia przeterminowanego zlecenia %s wymiany %s %s na %s %s.' % (self.seller, self.cryptocurrency_sold, self.amount_sold, self.cryptocurrency_bought, self.amount_bought)
                return 'Historia anulowanego zlecenia %s wymiany %s %s na %s %s. Zlecenie anulowano ' % (self.seller, self.cryptocurrency_sold, self.amount_sold, self.cryptocurrency_bought, self.amount_bought, self.commission_id, self.executed_time)
            return 'Historia niezrealizowanego zlecenia %s wymiany %s %s na %s %s. Nr powiązanego zlecenia %s.' % (self.seller, self.cryptocurrency_sold.name, self.amount_sold, self.cryptocurrency_bought.name, self.amount_bought, self.commission_id)
        return 'Historia między kupującym %s, a sprzedającym %s wymiany %s %s na %s %s.' % (self.purchaser, self.seller, self.cryptocurrency_sold.name, self.amount_sold, self.cryptocurrency_bought.name, self.amount_bought)
    
    @staticmethod
    def getAveragePrice(cryptocurrency_sold, cryptocurrency_bought, date_start, date_end, source_price=0):
        """
        Zwraca średnią cenę z okresu date_start - date_end dla wymienionej kryptowaluty cryptocurrency_sold za cryptocurrency_bought.
        source_price decyduje o tym, która cena kryptowaluty jest zwracana
        jeżeli source_price = 0 to cena cryptocurrency_sold w innym przypadku cryptocurrency_bought
        """
        if(not hasattr(cryptocurrency_sold, 'id')):
            cryptocurrency_sold = Cryptocurrency.objects.filter(name=cryptocurrency_sold)[0]
        if(not hasattr(cryptocurrency_bought, 'id')):
            cryptocurrency_bought = Cryptocurrency.objects.filter(name=cryptocurrency_bought)[0]
        
        coms = History.objects.extra(where=["purchaser_id is not null and cryptocurrency_sold_id = %s and cryptocurrency_bought_id %s and executed_time > %s and executed_time < %s"], params=[cryptocurrency_sold.id, cryptocurrency_bought.id, date_start, date_end])
        i = coms.count()
        sum=0
        if source_price == 0:
            for com in coms:
                sum+=com.sold_price
        else:
            for com in coms:
                sum+=com.bought_price
        if(i==0):
            return 0
        return sum/i

    @staticmethod
    def getAverageExchangePrice(cryptocurrency_first, cryptocurrency_second, date_start, date_end, source_price=0):
        """
        Zwraca średnią cenę z okresu date_start - date_end dla wymienionej kryptowaluty cryptocurrency_first za cryptocurrency_second bądź odwrotnie.
        source_price decyduje o tym, która cena kryptowaluty jest zwracana
        jeżeli source_price = 0 to cena cryptocurrency_sold w innym przypadku cryptocurrency_bought
        """
        if(not hasattr(cryptocurrency_first, 'id')):
            cryptocurrency_first = Cryptocurrency.objects.filter(name=cryptocurrency_first)[0]
        if(not hasattr(cryptocurrency_second, 'id')):
            cryptocurrency_second = Cryptocurrency.objects.filter(name=cryptocurrency_second)[0]
            
        coms = History.objects.extra(where=["((purchaser_id is not null and cryptocurrency_sold_id = %s and cryptocurrency_bought_id = %s) or (cryptocurrency_bought_id = %s and cryptocurrency_sold_id = %s)) and (executed_time > %s and executed_time < %s)"], params=[cryptocurrency_first.id, cryptocurrency_second.id,cryptocurrency_first.id, cryptocurrency_second.id, date_start, date_end])
        i = coms.count()
        sum=0
        if source_price == 0:
            for com in coms:
                if com.cryptocurrency_sold.id == cryptocurrency_first.id:
                    print 1
                    sum+=com.sold_price
                else: 
                    print 2
                    sum+=com.bought_price
        else:
            for com in coms:
                if com.cryptocurrency_sold.id == cryptocurrency_first.id:
                    print 3 
                    sum+=com.bought_price
                else: 
                    print 4
                    sum+=com.sold_price
                print com.executed_time
        if(i==0):
            return 0
        return sum/i
    
    
    @staticmethod
    def getAverageExchangePriceOfDay(cryptocurrency_first, cryptocurrency_second, date, source_price=0):
        """
        Zwraca średnią cenę z okresu date_start - date_end dla wymienionej kryptowaluty cryptocurrency_first za cryptocurrency_second bądź odwrotnie.
        source_price decyduje o tym, która cena kryptowaluty jest zwracana
        jeżeli source_price = 0 to cena cryptocurrency_sold w innym przypadku cryptocurrency_bought
        """
        date_start = datetime.datetime(date.year,date.month, date.day, 0,0,0)
        date_end = date_start+ datetime.timedelta(days=1)
        return History.getAverageExchangePrice(cryptocurrency_first=cryptocurrency_first, cryptocurrency_second=cryptocurrency_second, date_start=date_start, date_end=date_end, source_price=source_price)
    
class DepositHistory(models.Model):
    """
    Klasa histori przelewów użytkownika na giełdę, bądź z giełdy
    na zewnetrzne konta.
    Data executed_time czas kiedy nastąpiło zdarzenie
    Cryptocurrency cryptocurrency waluta
    String wallet_address adres na który, bądź z którego została pobrana waluta
    bool deposit określa czy skłądano depozyt czy pobierano walute z konta
    """
    user = models.ForeignKey(User, blank=False, unique=False)
    wallet_address = models.CharField(max_length="64", blank=False, unique=False)
    cryptocurrency = models.ForeignKey(Cryptocurrency, unique=False)
    amount = models.DecimalField(max_digits=32, decimal_places=16, blank=False, unique=False)
    executed_time = models.DateTimeField()
    deposit = models.BooleanField(blank=False, unique=False)
    
    def __unicode__(self):
        if(self.deposit is True):
            return 'Użytkownik %s złożył na portfel %s z adresu %s taką kwotą %s. Data: %s' % (self.user.username, self.cryptocurrency, self.wallet_address, self.amount, self.executed_time)
        if(self.deposit is False):
            return 'Użytkownik %s pobrał z portfela %s na adress %s taką kwotą %s. Data: %s' % (self.user.username, self.cryptocurrency, self.wallet_address, self.amount, self.executed_time)

class WithdrawCodes(models.Model):
    wallet = models.ForeignKey('UserWallet', blank=False, unique=False)
    code = models.CharField(max_length="32", blank=False, unique=True)

    @staticmethod
    def confirm(user, code, wallet_address, amount):
        hashs = hashlib.md5()
        hashs.update(code)
        code = hashs.hexdigest()
        if WithdrawCodes.objects.filter(code=code).exists():
            code = WithdrawCodes.objects.filter(code=code)[0]
            if(code.wallet.user.id is not user.id):
                raise Exception("Użytkownik %s nie jest zalogowany." % (code.user))
            wallet = UserWallet.objects.get(id = code.wallet.id)
            if(wallet.account_balance-Decimal(amount) < 0):
                raise Exception("Brakuje środków na portfelu %s. Na portfelu posiadasz jedynie %s, a chcesz wypłacić %s" % (wallet.cryptocurrency, wallet.account_balance, amount))
            wallet.account_balance = wallet.account_balance-Decimal(amount)
            wallet.save()
            code.delete()
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            deposit_history = DepositHistory(user=wallet.user, wallet_address=wallet_address, cryptocurrency=wallet.cryptocurrency, amount=amount, executed_time=now, deposit=False)
            deposit_history.save()
            return True
        else: 
            return False
        return 0
        
        
    def __unicode__(self):
        return 'Niepotwierdzone: %s' % (self.commission)
        
class UserWallet(models.Model):
    """
    Klasa podstawowa definiująca porfel użytkownika,
    rozszerzają jej możliwości proxy,
    ktore udostępniają metody do wpłaty i pobrania pieniędzy z portfela
    udostępiania metody do tworzenia zleceń, kupowania i pobierania pieniędzy
    """
    user = models.ForeignKey(User, blank=False, unique=False)
    account_balance = models.DecimalField(max_digits=32, decimal_places=16, blank=False)
    cryptocurrency = models.ForeignKey(Cryptocurrency, blank=False, unique=False)
    code = models.IntegerField(max_length="64", blank=True, unique=False, null=True)

    def __unicode__(self):
        return 'Portfel %s użytkownika %s posiadający %s' % (self.cryptocurrency.name, self.user.username, self.account_balance)

    def newPurchaseOffer(self, commission):
        """
        @param Commission : commission
        dodaje do bazy danych wpis o ofercie kupna,
        oraz odejmuje z konta potrzebną ilość gotówki,
        zapisuje użycie metody w historii
        """
        # sprawdzenie danych wejściowych
        # czy portfele należą do użytkownika, który wywołał funkcje
        if(commission.source_wallet.user.id is not self.user.id):
            raise Exception('Portfel source jest przypisany do innego użytkownika.')
        if(commission.destination_wallet.user.id is not self.user.id):
            raise Exception('Portfel destination jest przypisany do innego użytkownika.')
        # czy podane kwoty są poprawne
        if(Decimal(commission.source_amount) < 0):
            raise Exception('source_amount jest poniżej zera.')
        if(Decimal(commission.destination_amount) < 0):
            raise Exception('destination_amount jest poniżej zera.')
        if(Decimal(commission.source_amount) > Decimal(self.account_balance)):
            raise Exception('Brak środków na koncie. Posiadasz %s, a chcesz stworzyć za %s' % (self.account_balance, commission.source_amount))
        # pobranie kwoty z konta
        self.account_balance = UserWallet.objects.filter(id=self.id)[0].account_balance
        self.account_balance = Decimal(self.account_balance) - Decimal(commission.source_amount)
        # zapis do bazy danych
        self.save()
        # dodanei wpisu do historii
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        history = History(seller=self.user, commission_id=commission.id, cryptocurrency_sold=self.cryptocurrency, cryptocurrency_bought=commission.destination_wallet.cryptocurrency,
                           amount_sold=commission.source_amount, amount_bought=commission.destination_amount, create_time=now)
        history.save()
        return 0

    def purchase(self, purchased_offer):
        """
        @param Commission : purchased_offer
        dodaje do konta kwotę z zatwierdzonej oferty
        zapisuje użycie metody w historii
        """
        
        if(purchased_offer.source_wallet.cryptocurrency.id is self.cryptocurrency.id):
            self.account_balance = UserWallet.objects.filter(id=self.id)[0].account_balance
            self.account_balance = (self.account_balance) + Decimal(purchased_offer.source_amount)
        else:
            raise Exception("Błąd w metodzie purchase")
        return 0

    def purchaseSell(self, purchased_offer):
        """
        @param Commission : purchased_offer
        odejmuje z konta kwotę z zatwierdzonej oferty
        zapisuje użycie metody w historii
        """
        self.account_balance = UserWallet.objects.filter(id=self.id)[0].account_balance
        if(Decimal(self.account_balance) - Decimal(purchased_offer.destination_amount) < 0):
            raise Exception("Brakuje Tobie środków na portfelu %s. Na portfelu posiadasz jedynie %s, a chcesz wypłacić %s" % (self.cryptocurrency, self.account_balance, purchased_offer.destination_amount))
        if(purchased_offer.destination_wallet.cryptocurrency.id is self.cryptocurrency.id):
            self.account_balance = Decimal(self.account_balance) - Decimal(purchased_offer.destination_amount)
        else:
            raise Exception("Błąd w metodzie purchase sell")
        print purchased_offer.id
        print "cipa"
        history = History.objects.filter(commission_id=purchased_offer.id)
        history = history[0]
        history.purchaser = self.user
        history.save()
        
        return 0

    def sale(self, saled_offer):
        """
        @param Commission : saled_offer
        dodaje do konta kwotę z sprzedanej oferty
        zapisuje użycie metody w historii
        """
        # zakladajacy zlecenie
        if(saled_offer.destination_wallet.id is self.id):
            self.account_balance = UserWallet.objects.filter(id=self.id)[0].account_balance
            self.account_balance = Decimal(self.account_balance) + Decimal(saled_offer.destination_amount)
        else:
            raise Exception("Błąd w metodzie sale")
        # pobranie histori i uaktualnienie wpisu
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        
        
        history = History.objects.filter(commission_id=saled_offer.id)
        history = history[0]
        history.commission_id=None
        history.executed_time=now
        history.save()
        return 0
    
    def withdrawRequest(self, amount=None, wallet_address=None):
        """
        Wysyła maila potwierdzającego.
        """
        code=""
        for x in range(0,5):
            code+=str(random.randint(0,9))

        #sender = Smsapi("chrystian.kislo@gmail.com", "123sd890")
        #sender.sendConfirmationOfWithdraw(number=self.user.phone_number,code=code,id=deposit_history.id)
        print "Klucz %s" % code
        
        hashs = hashlib.md5()
        hashs.update(code)
        code = hashs.hexdigest()
        
        withdraw_codes = WithdrawCodes(wallet=self,code=code)
        withdraw_codes.save()
        return 0;
        
    def deposit(self, amount, wallet_address):
        """
        Zapisuje w historii.
        """
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.account_balance = UserWallet.objects.filter(id=self.id)[0].account_balance
        self.account_balance = self.account_balance + Decimal(amount)
        deposit_history = DepositHistory(user=self.user, wallet_address=wallet_address, cryptocurrency=self.cryptocurrency, amount=amount, executed_time=now, deposit=True)
        deposit_history.save()
        return 0;
    
    def incrementCode(self):
        self.code = self.code+1
        self.save()
        return self.code
#    class Meta:
#        """
#        @note: Ustawia klasę UserWallet jako klasa abstrakcyjna
#        """
#        abstract = True

class Provisions(models.Model):
    commission = models.ForeignKey(Commission, blank=False, unique=False)
    provision = models.DecimalField(max_digits=32, decimal_places=16, blank=False, null=False)
    
    def __unicode__(self):
        return "%s - prowizja %s" % (self.commission, self.provision) 
    
class AdminWallets():
    
    @staticmethod
    def addProvisionToCommission(commission):
        """
        Przesyla pieniadze dla administratora.
        """
        provision=Decimal('0.0025')
        if(commission.source_wallet.cryptocurrency.name=='BTC'):
            prov = commission.source_amount * Decimal(provision) 
            commission.source_amount += prov 
        elif (commission.destination_wallet.cryptocurrency.name=='BTC'):
            prov = commission.destination_amount * Decimal(provision)
            commission.destination_amount += prov
        commission.save()
        provision = Provisions(commission=commission, provision=prov)
        provision.save()
        return 0
    
    @staticmethod
    def takeProvision(commission):
        """
        Przesyla pieniadze dla administratora.
        """
        provision = Provisions.objects.filter(commission=commission)[0]
        if(commission.source_wallet.cryptocurrency.name=='BTC'):
            commission.source_amount -= provision.provision 
        elif (commission.destination_wallet.cryptocurrency.name=='BTC'):
            commission.destination_amount -= provision.provision
        user = UserProxy.objects.filter(username='admin')[0]
        btc_wallet = UserWallet.objects.filter(user=user, cryptocurrency=Cryptocurrency.objects.filter(name='BTC'))[0]
        btc_wallet.account_balance+=provision.provision
        btc_wallet.save()
        return 0


admin.site.register(UserProxy)
admin.site.register(Commission)
admin.site.register(History)
admin.site.register(DepositHistory)
admin.site.register(Cryptocurrency)
admin.site.register(WithdrawCodes)
admin.site.register(UserWallet)
admin.site.register(Provisions)