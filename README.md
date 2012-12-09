boxeeremotelib: python interface to the boxee remote api
==========================================================

Python library to use the [boxee remote api](http://developer.boxee.tv/Remote_Control_Interface). The library includes
functionality to discover servers via boxee's UDP-based discovery as well as an interface to the actual commands. The
intention of this project is to support a web interface to the remote and any other non-traditional uses. 

It is currently tested against a single boxee box and only on linux, so please share any negative results that you 
experience, but it should work more widely.

Scripts
--------

A couple of scripts are provided, *boxee_discover* and *boxee_command*. 

```````````````````````````````````````````
$ boxee_discover
192.168.1.104:8800
```````````````````````````````````````````

All servers on the network should be listed. A bit more functionality can be found with *boxee_command*:

```````````````````````````````````````````
$ boxee_command back setstring:batman
$ boxee_command down select
```````````````````````````````````````````

From the main menu, the previous example should go back to the search screen, type 'batman', and select 
the first result. It should be noted that the server is being auto-selected, but a specific server can be given

````````````````````````````````````````````````````````````
$ boxee_command --host=192.168.1.104 --port=8800 getvolume
100
````````````````````````````````````````````````````````````
In addition to the normal commands,

```````````````````````````````````````````````````````
$ boxee_command -l
back
backspace
down
getpercentage
getvolume
left
mute
pause
playnext
playprev
right
seekpercentage
seekpercentagerelative
select
setstring
setvolume
stop
up
````````````````````````````````````````````````````````

commands can be quickly repeated by adding '_n' on to the end of  a command name, where 'n' is the number 
of times to repeat the command. These repeat commands are available from the library as well.

```````````````````````````````````````````````````````
$ boxee_command backspace_6 setstring:misfits
```````````````````````````````````````````````````````

Authors
--------

Library written by Kali Norby <kali.norby@gmail.com>.

Thanks
-------

* Android [boxeeremote](http://code.google.com/p/boxeeremote/) - helpful guide, particularly for discovery