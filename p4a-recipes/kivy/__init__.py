from pythonforandroid.recipe import CythonRecipe


class KivyRecipe(CythonRecipe):
    version = '2.3.1'
    # 直接写死正确的 refs/tags 完整 URL，绕过 {version} 替换
    url = 'https://github.com/kivy/kivy/archive/refs/tags/2.3.1.zip'
    name = 'kivy'
    depends = ['sdl2', 'pyjnius']


recipe = KivyRecipe()
