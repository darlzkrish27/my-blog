---
layout: post
title:  "A response to Dropping Django"
date:   2009-08-20 17:28:37+05:30
categories: rambling
author: shabda
---
[Brandon Bloom](http://blog.brandonbloom.name/2009/08/dropping-django.html) yesterday wrote an interesting post titled
dropping Django. Despite a lot of hand waving(We needed a pragmatic template language to replace Django's idealistic one.),
it raises some valid questions, so here is a solution to some of them.

#### No support for hierarchical url creation.

The simplest representation of nested urls I can think of is a nested tuple. Lets represent,
the urls for a simple app by,

    >>> tree_urls = ('', 'list',
    ...     ('edit/', 'edit', ('auto/', 'edit_auto')),
    ...     ('^add/', 'add'),
    ...     ('delete/', 'delete', ('hard/', 'delete_hard'))
    ...     )
    
Guess what, urls.py is *just a python module which excepts a variable names urlpatterns*.

Which means it is very easy to write a function which converts this nested structure to flat, structure.
Here is a quick attempt at that,

    def merge(url):
        full_url=[]
        for i, el in enumerate(url):
            if i%2==0:    
                full_url.append(el)
        full_url = ''.join(full_url)
        return full_url
        
    def combineflatten(seq):
        items= tuple(item for item in seq if not isinstance(item, tuple))
        yield items
        for item in seq:
                if isinstance(item, tuple):
                    for yielded in combineflatten(item):
                        yield items+yielded
                        
    def generate_flat_urls(tree_urls):
        """
        >>> tree_urls = ('', 'list',
        ...     ('edit/', 'edit', ('auto/', 'edit_auto')),
        ...     ('^add/', 'add'),
        ...     ('delete/', 'delete', ('delete/', 'delete_hard'))
        ...     )
    
        >>> generate_flat_urls(tree_urls)
        [('^$', 'list'), ('^edit/$', 'edit'), ('^edit/auto/$', 'edit_auto'), ('^^add/$', 'add'), ('^delete/$', 'delete'), ('^delete/delete/$', 'delete_hard')]
        """
        return [('^%s$'%merge(el), el[-1]) for el in tuple(combineflatten(tree_urls))]

With this you can use hierarchical urls in urls.py as,

    #All of urls.py
    tree_urls = ('', 'list',
        ('edit/', 'edit', ('auto/', 'edit_auto')),
        ('^add/', 'add'),
        ('delete/', 'delete', ('delete/', 'delete_hard'))
        )
        
    flat_urls = generate_flat_urls(tree_urls)
    
    urlpatterns = patterns('app.views',
    **flat_urls
    )
    
#### No support for per user, per resource authorisation.

If you want to do this in a almost no-touching-the-existing-code way, replace all your `render_to_response` with,
    
    def render_with_auth_check(request, payload, request_context, *args, **kwrags):
        for el in payload.itervalues():
            try:
                has_auth = el.check_auth(request.user)
                if not has_auth:
                    raise AuthFailException
            except ValueError:
                pass #Not all objects have check_auth
        return render_to_response(request, payload, request_context, *args, **kwrags)
        
And enable this middleware,

    class AuthFailHandlerMiddleware:
        def process_exception(self, request, exception):
            if type(exception) == AuthFailException:
                return render_to_response('accounts/login/', {}, RequestContext(request))

        
This assumes that all resources which are authorisation protected have a `.check_auth`,
but I cant see any way round that in any other way as well.

A different, and more robust way would be to write custom managers for all resources, which need authorization.

    class ResourceAuthManager(models.Manager):
        def get(self, user, *args, **kwargs):
            res = super(ResourceAuthManager, self).get(*args, **kwargs)
            try:
                has_auth = res.check_auth(request.user)
                if not has_auth:
                    raise AuthFailException
            except ValueError:
                pass #Not all objects have check_auth
                
        ...

#### The Django templating language is too constrained.

Despite believing that Django templating language hits the sweet spot between, power
and convenience to *people who would be using it*, I never understood this argument,

If you are using sqlalchemy with Django you lose the admin, what do you lose if you use Jinja?

In particular what do you lose by replacing `render_to_response` with this,
    
    def render_jinja_to_response(template_name, payload):
        #This should probably go in settings.py
        from jinja2 import Environment
        env = Environment(loader=PackageLoader('app', 'templates'))
        
        template = env.get_template(template_name)
        response = template.render(**payload)
        return HttpResponse(response)

#### Extending authentication - In particular enable loggin in with email

Django authenticates against a [wide range of backends](http://www.google.co.in/search?hl=en&client=firefox-a&rls=org.mozilla%3Aen-US%3Aofficial&hs=GGQ&q=authentication+backends+site%3Adjangosnippets.org&btnG=Search&meta=&aq=f&oq=),
including Email, LDAP, Twitter and Facebook. While it is true that email backend doesn't work
with Admin login, Admin is meant for use by staff and superusers, so why cant we provide
them usernames?

There are a few other questions raised, some of which I agree with("Sadly, it[the admin app]
struggles a little bit with nullable fields and is tricky to customize."), and some which I dont,
("I will never write CSS by hand again." - You shouldn't be, someone else on your team should be doing that. )
But this line is interesting `Personally, I've developed a moderate fear of the word "framework"`.

This is arguable, but the way all frameworks essentially help you is by providing
Dependency Injection, (the Hollywood principle - Dont call me, I will call you).
Django provides that in a lot of ways. (You write a middleware, and django calls
it at appropriate places - Dont call me, I will call you), but still leaves something to be desired.
My ideal framework would be one where models are POPO and views are functions which return strings
. (Plain old python objects -like POJO). [JPA](http://java.sun.com/developer/technicalArticles/J2EE/jpa/figure6.html) does this correctly,
but then JPA has the typing information, so maybe in python the only way to provide the required typing
information is `name=models.CharField(...)`. But the point being, we need better Dependency Inversion,
not less of it. We have been dow that path earlier, and it is a much harder way to build complex systems.

-------
Resources

1. [This code on github](http://gist.github.com/171016)
2. [Discussion about converting the nested tuple to a flat one](http://stackoverflow.com/questions/1302653/convert-a-nested-dataset-to-a-flat-dataset-while-retaining-enough-data-to-conver)

--------
My apologies if this post was aggressive, argumentative or disrespectful to the
original author. We generally try to stay away from controversial posts on this blog. But
I believe that this post raised some valid technical questions, and the intent of this
post was to answer them. For Django to develop the best way, we need more of these kind
of "What is wrong with Django" posts, not less, so my thanks to the original author. :)

--------
Do you want to build **Amazing Web Apps**? [We can help](http://uswaretech.com/contact/).

