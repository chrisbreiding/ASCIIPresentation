# ASCII Presentation

Why use Sublime just to create presentations when you can also use it as the presentation tool?

Check out [my presentation on browserify](https://github.com/chrisbreiding/presentations/blob/master/browserify/presentation.pres) as an example.

![](http://i.imgur.com/wCKIgKvh.jpg)

![](http://i.imgur.com/EEhrLk7h.jpg)

Currently, this package simply gives you syntax highlighting for:

### Headings

```
##
Heading Here
##
```

### Sub-headings

```
Sub-Heading Here ##
```

### Lists
```
- a list item
- another item
  * a sub item
  * another sub item
- a final item
```

### ASCII terminal

```
 -----------------------------------
|ooo                                |
|-----------------------------------|
|                                   |
|$ echo "this looks pretty nice"    |
|                                   |
|                                   |
|                                   |
 -----------------------------------
```

For the ASCII headings in the [browserify presentation](https://github.com/chrisbreiding/presentations/blob/master/browserify/presentation.pres), I used [http://patorjk.com/software/taag/](http://patorjk.com/software/taag/).

In the future, I hope to add some functionality to the package so that it can automatically create ASCII headings for you with just a keyboard shortcut.

## Installation

1 - Clone this repo into your Sublime Text Packages directory.

2 - Add the following to your color scheme:

  ```
    <dict>
      <key>name</key>
      <string>ascii_presentation.invisible</string>
      <key>scope</key>
      <string>ascii_presentation.invisible</string>
      <key>settings</key>
      <dict>
        <key>foreground</key>
        <string>#141414</string>
      </dict>
    </dict>
    <dict>
      <key>name</key>
      <string>ascii_presentation.close</string>
      <key>scope</key>
      <string>ascii_presentation.close</string>
      <key>settings</key>
      <dict>
        <key>foreground</key>
        <string>#BE2E2E</string>
      </dict>
    </dict>
    <dict>
      <key>name</key>
      <string>ascii_presentation.minimize</string>
      <key>scope</key>
      <string>ascii_presentation.minimize</string>
      <key>settings</key>
      <dict>
        <key>foreground</key>
        <string>#BFA22E</string>
      </dict>
    </dict>
    <dict>
      <key>name</key>
      <string>ascii_presentation.expand</string>
      <key>scope</key>
      <string>ascii_presentation.expand</string>
      <key>settings</key>
      <dict>
        <key>foreground</key>
        <string>#70A340</string>
      </dict>
    </dict>
    <dict>
      <key>name</key>
      <string>ascii_presentation.chrome</string>
      <key>scope</key>
      <string>ascii_presentation.chrome</string>
      <key>settings</key>
      <dict>
        <key>foreground</key>
        <string>#777</string>
      </dict>
    </dict>
  ```
3 - Update the ascii_presentation.invisible color to match the background of your color scheme. Tweak other colors as desired.

## Use

Use the syntax enumerated above to create headings, lists, etc. I found putting 20 lines between 1 "slide" and another worked well for separating them if you'll be presenting on a typical 800x600 resolution projector.

By default, the syntax highlighting works with files with the extension `pres`.

## Modification

If you'd like to hack on the syntax definition, edit the `ASCIIPresentation.JSON-tmLanguage` file. Check out the [syntax definition docs](http://docs.sublimetext.info/en/latest/extensibility/syntaxdefs.html) for more info.

Pull requests are welcome!
