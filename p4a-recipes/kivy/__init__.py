from pythonforandroid.recipe import CythonRecipe


class KivyRecipe(CythonRecipe):
    version = '2.3.1'
    url = 'https://github.com/kivy/kivy/archive/refs/tags/2.3.1.zip'
    name = 'kivy'
    depends = ['sdl2', 'pyjnius']


recipe = KivyRecipe()
