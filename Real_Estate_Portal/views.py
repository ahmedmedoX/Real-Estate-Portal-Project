from django.shortcuts import render, redirect, HttpResponse
from .models import Property,Profile,Favorite
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm
from django.db.models import Q
from django.core.paginator import Paginator
import requests,json
from decimal import Decimal
import cv2
import numpy as np

def loggedin(request):
    auth=False
    if request.user.is_authenticated:
        auth=True
    return auth

def search_selection(property_type_,Bathrooms_,Bedrooms_,Price_,Listing_,text_search,Sort_):
    x1=["",""]  #2,7,6,6,6
    x2=["","","","","","","",""]
    x3=["","","","","","",""]
    x4=["","","","","","",""]
    x5=["","","","","","",""]
    x6=["","","",""]
    select=[]

    Listing=['1','0']
    property_type=[None,"0",'Apartment','Villa','House','Office','Studio','Shop']
    Bathrooms=[None,"0",'1','2','3','4','5']
    Bedrooms=[None,"0",'1','2','3','4','5']
    Price=[None,"0","1-4","4-10","10-15","15-30","+30"]
    Sort=[None,"id","price","-price"]

    j=0
    for i in Listing:
        if i == Listing_:
            x1[j]='selected'
            break
        j+=1
    j=0
    for i in property_type:
        if i == property_type_:
            x2[j]='selected'
            break
        j+=1
    j=0
    for i in Bathrooms:
        if i == Bathrooms_:
            x3[j]='selected'
            break
        j+=1
    j=0
    for i in Bedrooms:
        if i == Bedrooms_:
            x4[j]='selected'
            break
        j+=1
    j=0
    for i in Price:
        if i == Price_:
            x5[j]='selected'
            break
        j+=1
        j=0
    j=0
    for i in Sort:
        if i == Sort_:
            x6[j]='selected'
            break
        j+=1
    if text_search==None:
        text_search=''
    select.insert(0,x1)
    select.insert(1,x2)
    select.insert(2,x3)
    select.insert(3,x4)
    select.insert(4,x5)
    select.insert(5,text_search)
    select.insert(6,x6)
    return select

#Algorithms
#Properties Duplcation Detection Algorithm    

def check_duplication(latitude,longitude,floor_number,apartment_number):
    latitude=float(latitude)
    longitude=float(longitude)
    if Property.objects.filter(Q (apartment_number=apartment_number) & 
                               Q (floor_number=floor_number) & 
                               Q (longitude__range=(longitude-0.001,longitude+0.001)) &
                               Q (latitude__range=(latitude-0.001,latitude+0.001))).exists():
        return False
    return True

#Display Properties Algorithm
def Properties_Views(g,request):
    properties=[]
    for i in g: 
        tmp=[]
        y=str(i.price)
        y=y[::-1]
        z=str(int(((i.price)/(i.installment_years))/12))
        z=z[::-1]
        if len(z)>=7:
         price_per_year_=z[0:3]+','+z[3:6]+','+z[6:]
        else:
         price_per_year_=z[0:3]+','+z[3:]
        if len(y)==5:
            price_=y[3:6]+','+y[6:9]+','+y[9:]
        else:
            price_=y[3:6]+','+y[6:9]+','+y[9:]
        price_=price_[::-1]
        price_per_year_=price_per_year_[::-1]
        tmp.append(i)
        tmp.append(price_)
        tmp.append(price_per_year_)
        # for j in range(7):
        properties.append(tmp)      
    p = Paginator(properties,4)
    page = request.GET.get('page')
    paging= p.get_page(page)
    return paging

#Recommendation Algorithm
def recommended_properties(request,id):
    request_data = request.GET.get('v')
    if request_data!=None:
        request_data=request_data.split()
        latitude=float(request_data[0])
        longitude=float(request_data[1])
        i=0.01
        while True:
            x = Property.objects.filter(Q (longitude__range=(longitude-i,longitude+i)) & 
                                        Q (latitude__range=(latitude-i,latitude+i))).exclude(id=id)
            if len(x)<2:
                i +=0.005
                if i==0.05:
                    break
            else:
                break
    else:
        if loggedin(request):
            user = request.user
            profile=Profile.objects.get(user=user)
            x = Property.objects.filter(city=profile.city).exclude(id=id)
        else:
            x = Property.objects.all().exclude(id=id)
            x=[x.first(),x.last()]
    
    if len(x)==1:
        x.append(Property.objects.order_by('?').exclude(id=id).first())
    elif len(x)==0:
        x = Property.objects.order_by('?').exclude(id=id)[:2]
        
    return x[:2]

# Create your views here.
#
def home(request):
    Category=[
    ('APARTMENT','Apartment'),
    ('VILLA','Villa'),
    ('HOUSE','House'),
    ('OFFICE','Office'),
    ('STUDIO','Studio'),
    ('SHOP','Shop')
    ]

    count=[]
    for j in Category:
       count.append(len(Property.objects.filter(category=j[0])))
    
    properties=[]
    price_Dictionary={
       '1-4':[0,4000000],
       '4-10':[4000000,10000000],
       '10-15':[10000000,15000000],
       '15-30':[15000000,30000000],
       '+30':[30000000,99999999999]
    }
    Price_=Bedrooms_=Bathrooms_=property_type_=text_search=Listing_=Sort_=None
    data=None
    if loggedin(request):
        user=request.user
        g=Favorite.objects.filter(user_ID=user.id)
        x={}
        p=0
        for i in g:
            k=Property.objects.get(pk=i.property_ID)
            x[p]=k.id
            p+=1
        data=json.dumps(x)
    if request.method=='POST':
        property_type_=request.POST.get('property_type')
        Bathrooms_=request.POST.get('Bathrooms')
        Bedrooms_=request.POST.get('Bedrooms')
        Price_=request.POST.get('Price')
        Listing_=request.POST.get('Listing')
        text_search=request.POST.get('search_input')
        Sort_=request.POST.get('Sort')

        if property_type_==None and Bathrooms_==None and Bedrooms_==None and Price_==None and text_search==None:
            g=Property.objects.filter(Buy=Listing_)
        else:
            s1=s2=s3=s4=s5=s6=Property.objects.filter(Buy=Listing_)

            if property_type_!=None:
                s1=Property.objects.filter(category=property_type_.upper())
                if property_type_=='0':
                    s1=s6

            if Bathrooms_!=None:
                s2=Property.objects.filter(Bathrooms=Bathrooms_)
                if Bathrooms_=='0':
                    s2=s6

            if Bedrooms_!=None:
                s3=Property.objects.filter(Bedrooms=Bedrooms_)
                if Bedrooms_=='0':
                    s3=s6

            if Price_!=None:
                s4=Property.objects.filter(price__range=(price_Dictionary[Price_][0],price_Dictionary[Price_][1]))
            
            if text_search!=None: #__contains
                text_search=text_search
                s5=Property.objects.filter(Q(city__contains=text_search) | Q(name__contains=text_search) |
                                           Q(category__contains=text_search) | Q(description__contains=text_search))

            g=s1.intersection(s2,s3,s4,s5)
        if Sort_==None:
            g=g.order_by('id')
        else:
            g=g.order_by(Sort_)
        properties=Properties_Views(g,request)
        selection=search_selection(property_type_,Bathrooms_,Bedrooms_,Price_,Listing_,text_search,Sort_)
        return render(request, 'search.html', {'properties':properties,'loggedin':loggedin(request),'selection':selection,'data':data,'b':[0,1,0,0]})
    else:
        properties=Properties_Views(recommended_properties(request,9999),request)
        return render(request, 'index1.html', {'properties':properties,'loggedin':loggedin(request),'count':count,'data':data,'b':[1,0,0,0]})
# 
def login_user(request):
    if loggedin(request):
        return redirect('profile')
    else:
        if request.method=='POST':
            password=request.POST['password']
            username=request.POST['username']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, ("You have been logged in!"))
                return redirect('home')
            else:
                messages.success(request, ("Username or Password is incorrect!"))
                return redirect('login')
        else:
            return render(request, 'login.html', {})
#
def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out!"))
    return redirect('home')
#
def sign_up(request):
    if loggedin(request):
        return redirect('profile')
    else:
        form=CreateUserForm()
        return render(request, 'sign_up.html', {'form':form})
#
def sign_up2(request):
    if request.method=="POST":
        form=CreateUserForm(request.POST)
        try:
            if form.is_valid():
                form.save()
                username=form.cleaned_data['username']
                password=form.cleaned_data['password1']
                user=authenticate(username=username,password=password)
                login(request, user)
                user = request.user

                phone=request.POST['phone']
                street=request.POST['street']
                city=request.POST['city']

                profile=Profile.objects.get(user=user)
                profile.phone=phone
                profile.street=street
                profile.city=city
                profile.save()
                messages.success(request,('You have been registered!'))
                return redirect('home')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request,f'{field.capitalize()}:{error}')
        except Exception as e:
            messages.error(request,f'Signup failed, an error has occured: {str(e)}')
            return redirect('sign_up')
    return redirect('sign_up')
#
def search(request):
    properties=[]
    price_Dictionary={
        '0':[0,9999999999],
       '1-4':[0,4000000],
       '4-10':[4000000,10000000],
       '10-15':[10000000,15000000],
       '15-30':[15000000,30000000],
       '+30':[30000000,99999999999]
    }
    Price_=Bedrooms_=Bathrooms_=property_type_=text_search=Listing_=Sort_=None

    if request.method=='POST':
        property_type_=request.POST.get('property_type')
        Bathrooms_=request.POST.get('Bathrooms')
        Bedrooms_=request.POST.get('Bedrooms')
        Price_=request.POST.get('Price')
        Listing_=request.POST.get('Listing')
        text_search=request.POST.get('search_input')
        Sort_=request.POST.get('Sort')

        if property_type_==None and Bathrooms_==None and Bedrooms_==None and Price_==None and text_search==None:
            g=Property.objects.filter(Buy=Listing_)
        else:
            s1=s2=s3=s4=s5=s6=Property.objects.filter(Buy=Listing_)

            if property_type_!=None:
                if property_type_=='0':
                    s1=s6
                else:
                    s1=Property.objects.filter(category=property_type_.upper())
                
            if Bathrooms_!=None:
                if Bathrooms_=='0':
                    s2=s6
                else:
                    s2=Property.objects.filter(Bathrooms=Bathrooms_)
                
            if Bedrooms_!=None:
                if Bedrooms_=='0':
                    s3=s6
                else:
                    s3=Property.objects.filter(Bedrooms=Bedrooms_)
                
            if Price_!=None:
                s4=Property.objects.filter(price__range=(price_Dictionary[Price_][0],price_Dictionary[Price_][1]))
            
            if text_search!=None: #__contains
                text_search=text_search
                s5=Property.objects.filter(Q(city__contains=text_search) | Q(name__contains=text_search) |
                                           Q(category__contains=text_search) | Q(description__contains=text_search))

            g=s1.intersection(s2,s3,s4,s5)
    else:
        g=Property.objects.filter(Buy=True)

    if Sort_==None:
        g=g.order_by('id')
    else:
        g=g.order_by(Sort_)
    properties=Properties_Views(g,request)
    selection=search_selection(property_type_,Bathrooms_,Bedrooms_,Price_,Listing_,text_search,Sort_)
    data=None
    if loggedin(request):
        user=request.user
        g=Favorite.objects.filter(user_ID=user.id)
        x={}
        p=0
        for i in g:
            k=Property.objects.get(pk=i.property_ID)
            x[p]=k.id
            p+=1
        data=json.dumps(x)
    return render(request, 'search.html', {'properties':properties,'loggedin':loggedin(request),'selection':selection,'data':data,'b':[0,1,0,0]})
#
def property(request,id):
    property=[]
    tmp=[]
    g=Property.objects.get(id=id)
    address_URL = requests.get('https://geocode.maps.co/reverse?lat='+str(g.latitude)+'&lon='+str(g.longitude)+'&api_key=65eb0c3aaeec6728883009grv7d2276')
    address = address_URL.json()
    tmp=[]
    y=str(g.price)
    y=y[::-1]
    z=str(int(((g.price)/(g.installment_years))/12))
    z=z[::-1]    
    if len(z)>=7:
     price_per_year_=z[0:3]+','+z[3:6]+','+z[6:]
    else:
     price_per_year_=z[0:3]+','+z[3:]
    
    price_=y[3:6]+','+y[6:9]+','+y[9:]    
    price_=price_[::-1]
    price_per_year_=price_per_year_[::-1]
    tmp.append(g)
    tmp.append(price_)
    tmp.append(price_per_year_)
    tmp.append(address['display_name'])
    
    c=False
    if len(g.description) >= 300:
       c=True
    tmp.append(c)
    k='https://maps.google.com/maps?q='+str(g.latitude)+','+str(g.longitude)+'&hl=en&z=12&output=embed'
    tmp.append(k)

    property.append(tmp)
    #0=Property Query,1=Price,2=Price/year,3=Address
    properties=Properties_Views(recommended_properties(request,g.id),request)
    
    user=request.user
    g=Favorite.objects.filter(user_ID=user.id)
    x={}
    p=0
    for i in g:
        k=Property.objects.get(pk=i.property_ID)
        x[p]=k.id
        p+=1
    data=json.dumps(x)
    return render(request, 'property.html', {'properties':properties,'property':property,'loggedin':loggedin(request),'data':data})
#
def type_search(request, type):
    s=Property.objects.filter(category=type.upper())
    properties=Properties_Views(s,request)
    user=request.user
    g=Favorite.objects.filter(user_ID=user.id)
    x={}
    p=0
    for i in g:
        k=Property.objects.get(pk=i.property_ID)
        x[p]=k.id
        p+=1
    data=json.dumps(x)
    return render(request, 'search.html', {'properties':properties,'loggedin':loggedin(request),'data':data,'b':[0,1,0,0]})
#
def area_search(request, area):
    s=Property.objects.filter(Q(city__contains=area) | Q(name__contains=area) |
                               Q(category__contains=area) | Q(description__contains=area))
    properties=Properties_Views(s,request)
    user=request.user
    g=Favorite.objects.filter(user_ID=user.id)
    x={}
    p=0
    for i in g:
        k=Property.objects.get(pk=i.property_ID)
        x[p]=k.id
        p+=1
    data=json.dumps(x)
    return render(request, 'search.html', {'properties':properties,'loggedin':loggedin(request),'data':data,'b':[0,1,0,0]})
#
def contact_us(request):
    return render(request, 'contact_us.html', {'loggedin':loggedin(request),'b':[0,0,0,1]})
#
def list_property(request):
    if loggedin(request):
        return render(request, 'sell.html',{'loggedin':True})
    else:
        return redirect('sign_up')
#
def rent_property(request):
    if loggedin(request):
        return render(request, 'rent.html',{'loggedin':True})
    else:
        return redirect('sign_up')
#
def profile(request):
    if loggedin(request):
        user = request.user
        profile=Profile.objects.get(user=user)
        return render(request, 'profile.html',{'loggedin':True,'user':user,'profile':profile})
    else:
        return redirect('login')
#
def update_profile(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        phone=request.POST['phone']
        street=request.POST['street']
        city=request.POST['city']

        user=request.user
        user.username=username
        user.email=email
        profile=Profile.objects.get(user=user)
        profile.phone=int(phone)
        profile.street=street
        profile.city=city
        user.save()
        profile.save()
        messages.success(request,'Your Account has been updated!')
        return redirect('home')
    else:
        return redirect('home')
#
def about(request):
    return render(request, 'about.html',{'loggedin':loggedin(request),'b':[0,0,1,0]})
#
def add_favourite(request):
    if loggedin(request):
        data = request.GET.get('id')
        x = request.GET.get('x')
        user=request.user
        f=Favorite.objects.filter(property_ID=int(data),user_ID=user.id)
        if f.exists() :
            Favorite.objects.get(property_ID=int(data),user_ID=user.id).delete()
        else:
            fav=Favorite(user_ID=user.id,property_ID=int(data))
            fav.save()
        return HttpResponse('True')
    else:
        return redirect('sign_up')
#
def favorite(request):
    if loggedin(request):
        user=request.user
        g=Favorite.objects.filter(user_ID=user.id)
        x=[]
        for i in g:
            k=Property.objects.get(pk=i.property_ID)
            x.append(k)
        properties=Properties_Views(x,request)
        return render(request,'favourite.html',{'properties':properties,'loggedin':loggedin(request)})
    else:
        return redirect('sign_up')
#
def delete_confirm(request):
    if loggedin(request):
        return render(request,'delete_confirm.html',{'loggedin':True})
    else:
        return redirect('sign_up')
#
def delete_account(request):
    if loggedin(request):
        user=request.user
        Favorite.objects.filter(user_ID=user.id).delete()
        Property.objects.filter(seller_ID=user.id).delete()
        logout(request)
        messages.success(request, ("Your account have been deleted!"))
        user.delete()
        return redirect('home')
    else:
        return redirect('sign_up')
#Sell
def insert_property(request):
    user = request.user
    if request.method=='POST':
        floor_number=request.POST['floor_number']
        apartment_number=request.POST['apartment_number']
        Installment_years=request.POST['Installment_years']
        price=request.POST['price']
        name=request.POST['name']
        category=request.POST.get('category')
        description=request.POST['description']
        size=request.POST['size']
        Bedrooms=request.POST['Bedrooms']
        Bathrooms=request.POST['Bathrooms']
        image1=request.FILES['image1']
        image2=request.FILES['image2']
        image3=request.FILES['image3']
        latitude=request.POST['latitude']
        longitude=request.POST['longitude']
        
        if check_duplication(latitude,longitude,floor_number,apartment_number):
            address_URL = requests.get('https://geocode.maps.co/reverse?lat='+str(latitude)+'&lon='+str(longitude)+'&api_key=65eb0c3aaeec6728883009grv7d2276')
            address = address_URL.json()

            property=Property(name=name,price=price,installment_years=Installment_years,
                              apartment_number=apartment_number,size=size,category=category.upper(),
                              description=description,Bedrooms=Bedrooms,Bathrooms=Bathrooms,
                              floor_number=floor_number,Buy=False, seller_ID=user.id,
                              image1=image1,image2=image2,image3=image3,latitude=latitude,
                              longitude=longitude,city=address['address']['city'])
            property.save()
            messages.success(request,('The property has been listed!'))
            return redirect('profile')
        else:
            messages.success(request,('This property is already listed!'))
            return redirect('list_property')
    else:
        return redirect('home')
#Buy
def insert_property(request):
    user = request.user
    if request.method=='POST':
        floor_number=request.POST['floor_number']
        apartment_number=request.POST['apartment_number']
        Installment_years=request.POST['Installment_years']
        price=request.POST['price']
        name=request.POST['name']
        category=request.POST.get('category')
        description=request.POST['description']
        size=request.POST['size']
        Bedrooms=request.POST['Bedrooms']
        Bathrooms=request.POST['Bathrooms']
        image1=request.FILES['image1']
        image2=request.FILES['image2']
        image3=request.FILES['image3']
        latitude=request.POST['latitude']
        longitude=request.POST['longitude']

        if check_duplication(latitude,longitude,floor_number,apartment_number):
            address_URL = requests.get('https://geocode.maps.co/reverse?lat='+str(latitude)+'&lon='+str(longitude)+'&api_key=65eb0c3aaeec6728883009grv7d2276')
            address = address_URL.json()
            try:
                cit=address['address']['city']
            except:
                cit=address['address']['state']
                
            property=Property(name=name,price=price,installment_years=Installment_years,
                              apartment_number=apartment_number,size=size,category=category.upper(),
                              description=description,Bedrooms=Bedrooms,Bathrooms=Bathrooms,
                              floor_number=floor_number,Buy=True, seller_ID=user.id,
                              image1=image1,image2=image2,image3=image3,latitude=latitude,
                              longitude=longitude,city=cit)
            property.save()
            messages.success(request,('The property has been listed!'))
            return redirect('profile')
        else:
            messages.success(request,('This property is already listed!'))
            return redirect('list_property')
    else:
        return redirect('home')
#
def your_properties(request):
    if loggedin(request):
        user=request.user
        g=Property.objects.filter(seller_ID=user.id)
        properties=Properties_Views(g,request)
        return render(request,'your_properties.html',{'properties':properties,'loggedin':loggedin(request)})
    else:
        return redirect('sign_up')
#   
def edit_property(request,id):
    if loggedin(request):
        user=request.user
        g=Property.objects.filter(id=id)
        if user.id == g[0].seller_ID:
            x2=["","","","","",""]
            property_type=['APARTMENT','VILLA','HOUSE','OFFICE','STUDIO','SHOP']
            j=0
            for i in property_type:
                if g[0].category == i:
                    x2[j]='selected'
                    break
                j+=1
            x={
                'lat':str(g[0].latitude),
                'lon':str(g[0].longitude)
            }
            properties=Properties_Views(g,request)
            data=json.dumps(x)
            return render(request,'edit_property.html',{'properties':properties,'loggedin':loggedin(request),'data': data,'selection':x2})
        else:
            return redirect('profile')
    else:
        return redirect('sign_up')    
#
def update_property(request,id):
    if request.method=='POST':
        image1=image2=image3=None
        floor_number=request.POST['floor_number']
        apartment_number=request.POST['apartment_number']
        Installment_years=request.POST['Installment_years']
        price=request.POST['price']
        name=request.POST['name']
        category=request.POST.get('category')
        description=request.POST['description']
        size=request.POST['size']
        Bedrooms=request.POST['Bedrooms']
        Bathrooms=request.POST['Bathrooms']
        image1=request.FILES.get('image1')
        image2=request.FILES.get('image2')
        image3=request.FILES.get('image3')
        latitude=request.POST['latitude']
        longitude=request.POST['longitude']

        property=Property.objects.get(id=id)

        if int(floor_number)!=property.floor_number or int(apartment_number)!= property.apartment_number or Decimal(latitude)!=property.latitude or Decimal(longitude)!=property.longitude:
            address_URL = requests.get('https://geocode.maps.co/reverse?lat='+str(latitude)+'&lon='+str(longitude)+'&api_key=65eb0c3aaeec6728883009grv7d2276')
            address = address_URL.json()
            if check_duplication(latitude,longitude,floor_number,apartment_number):
                property.name=name
                property.price=price
                property.installment_years=Installment_years
                property.apartment_number=apartment_number
                property.size=size
                property.category=category.upper()
                property.description=description
                property.Bedrooms=Bedrooms
                property.Bathrooms=Bathrooms
                property.floor_number=floor_number

                if image1!=None:
                    property.image1=image1
                if image2!=None:
                    property.image2=image2
                if image3!=None:
                    property.image3=image3

                property.latitude=latitude
                property.longitude=longitude
                try:
                    property.city=address['address']['city']
                except:
                    property.city=address['address']['state']

                property.save()
                messages.success(request,('The property listing has been updated!'))
                return redirect('your_properties')
            else:
                messages.success(request,('This property is already listed!'))
                return redirect('edit_property',id=id)
        else:
            property.name=name
            property.price=price
            property.installment_years=Installment_years
            property.size=size
            property.category=category.upper()
            property.description=description
            property.Bedrooms=Bedrooms
            property.Bathrooms=Bathrooms
            if image1!=None:
                property.image1=image1
            if image2!=None:
                property.image2=image2
            if image3!=None:
                property.image3=image3
            property.save()
            messages.success(request,('The property listing has been updated!'))
            return redirect('your_properties')
    else:
        return redirect('home')
#
def delete_property(request,id):
    if loggedin(request):
        user=request.user
        g=Property.objects.filter(id=id)
        if user.id == g[0].seller_ID:
            if loggedin(request):
                return render(request,'delete_property_confirm.html',{'loggedin':True,'id':id})
        else:
            return redirect('your_properties')
    return redirect('sign_up')
#         
def delete_property_confirm(request,id):
    if loggedin(request):
        user=request.user
        g=Property.objects.filter(id=id)
        if user.id==g[0].seller_ID:
            if g.exists():
                for i in g:
                    Favorite.objects.filter(property_ID=i.id).delete()
                g.delete()
                messages.success(request,('The property has been deleted!'))
        return redirect('your_properties')
    else:
        return redirect('sign_up')
#
def delete_all(request):
    if loggedin(request):
        return render(request,'delete_all_confirm.html',{'loggedin':loggedin(request)})
    else:
        return redirect('sign_up')
#
def delete_all_confirm(request):
    if loggedin(request):
        user=request.user
        Favorite.objects.filter(user_ID=user.id).delete()
        Property.objects.filter(seller_ID=user.id).delete()
    return redirect('your_properties')
