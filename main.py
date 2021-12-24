
#mengimport yang di butuhkan
from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, TextNode
from panda3d.core import PointLight, AmbientLight
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.interval.SoundInterval import SoundInterval
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectButton import DirectButton
from direct.interval.MetaInterval import Parallel
from direct.interval.LerpInterval import LerpHprInterval
import sys

# Buat instance ShowBase, yang akan membuka jendela dan mengatur
# grafik pemandangan dan kamera.
base = ShowBase()

class MusicBox(DirectObject):
    def __init__(self):
        # Judul standar dan teks instruksi kami
        self.title = OnscreenText(text="Intan Naumi - V3920028",
                                  parent=base.a2dBottomCenter,
                                  pos=(0, 0.08), scale=0.08,
                                  fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.escapeText = OnscreenText(text="ESC: Quit", parent=base.a2dTopLeft,
                                       fg=(1, 1, 1, 1), pos=(0.06, -0.1),
                                       align=TextNode.ALeft, scale=.05)

        # Atur input kunci
        self.accept('escape', sys.exit)

        # Perbaiki posisi kamera
        base.disableMouse()

        # Memuat suara dilakukan dengan cara yang mirip dengan memuat hal-hal lain
        # Memuat lagu kotak musik utama
        self.musicBoxSound = loader.loadMusic('music/musicbox.ogg')
        self.musicBoxSound.setVolume(.5)  # Volume adalah persentase dari 0 hingga 1
        # 0 berarti loop selamanya, 1 (default) berarti
        # mainkan sekali. 2 atau lebih tinggi berarti mainkan berkali-kali
        self.musicBoxSound.setLoopCount(0)

        # Siapkan lampu sederhana.
        self.plight = PointLight("light")
        self.plight.setColor((0.7, 0.7, 0.5, 1))
        light_path = base.render.attachNewNode(self.plight)
        light_path.setPos(0, 0, 20)
        base.render.setLight(light_path)

        alight = AmbientLight("ambient")
        alight.setColor((0.3, 0.3, 0.4, 1))
        base.render.setLight(base.render.attachNewNode(alight))

        # Aktifkan pencahayaan per piksel
        base.render.setShaderAuto()


        # Objek suara tidak memiliki fungsi jeda, cukup putar dan hentikan. Jadi kita akan
        # Gunakan variabel ini untuk melacak di mana suara berada saat dihentikan
        # untuk menyiratkan jeda
        self.musicTime = 0


        # Memuat efek buka/tutup
        # loadSFX dan loadMusic identik. Mereka sering digunakan untuk organisasi
        #(loadMusic digunakan untuk musik latar, loadSfx digunakan untuk efek lainnya)
        self.lidSfx = loader.loadSfx('music/openclose.ogg')
        
        # File buka/tutup memiliki kedua efek di dalamnya. Untungnya kita bisa menggunakan interval
        # untuk dengan mudah menentukan bagian dari file suara untuk diputar
        self.lidOpenSfx = SoundInterval(self.lidSfx, duration=2, startTime=0)
        self.lidCloseSfx = SoundInterval(self.lidSfx, startTime=5)

        # Untuk tutorial ini, sepertinya tepat untuk memiliki kontrol di layar.
        # Kode berikut membuatnya.
        # Ini adalah label untuk penggeser
        self.sliderText = OnscreenText("Volume", pos=(-0.1, 0.87), scale=.07,
                                       fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

        # Penggeser itu sendiri. Itu memanggil self.setMusicBoxVolume ketika diubah
        self.slider = DirectSlider(pos=(-0.1, 0, .75), scale=0.8, value=.50,
                                   command=self.setMusicBoxVolume)
        # Tombol yang memanggil self.toggleMusicBox saat ditekan
        self.button = DirectButton(pos=(.9, 0, .75), text="Open",
                                   scale=.1, pad=(.2, .2),
                                   rolloverSound=None, clickSound=None,
                                   command=self.toggleMusicBox)

        # Sebuah variabel untuk mewakili keadaan simulasi. Ini mulai ditutup
        self.boxOpen = False

        # Di sini kita memuat dan mengatur kotak musik. Itu dimodelkan dengan cara yang kompleks, jadi
        # pengaturannya akan rumit
        self.musicBox = loader.loadModel('models/MusicBox')
        self.musicBox.setPos(0, 60, -9)
        self.musicBox.reparentTo(render)

        # Sama seperti grafik adegan yang berisi hierarki node, begitu juga
        # model. Anda bisa mendapatkan NodePath untuk node menggunakan find
        # fungsi, dan kemudian Anda dapat menganimasikan model dengan menggerakkan bagian-bagiannya
        # Untuk melihat hierarki model, gunakan fungsi ls
        # self.musicBox.ls() mencetak seluruh hierarki model

        # Menemukan potongan model
        self.Lid = self.musicBox.find('**/lid')
        self.Panda = self.musicBox.find('**/turningthing')

        # Model ini dibuat dengan engsel di tempat yang salah
        # ini di sini jadi kita harus mengubah sesuatu
        self.HingeNode = self.musicBox.find(
            '**/box').attachNewNode('nHingeNode')
        self.HingeNode.setPos(.8659, 6.5, 5.4)
        self.Lid.wrtReparentTo(self.HingeNode)
        self.HingeNode.setHpr(0, 90, 0)

        # Ini mengatur interval untuk memainkan suara dekat dan benar-benar menutup kotak
        # pada waktu bersamaan.
        self.lidClose = Parallel(
            self.lidCloseSfx,
            LerpHprInterval(self.HingeNode, 2.0, (0, 90, 0), blendType='easeInOut'))

        # Hal yang sama untuk membuka kotak
        self.lidOpen = Parallel(
            self.lidOpenSfx,
            LerpHprInterval(self.HingeNode, 2.0, (0, 0, 0), blendType='easeInOut'))

        # Interval untuk memutar panda
        self.PandaTurn = self.Panda.hprInterval(7, (360, 0, 0))

        # Lakukan loop cepat dan jeda untuk mengaturnya sebagai interval pengulangan sehingga bisa
        # dimulai dengan resume dan loop dengan benar
        self.PandaTurn.loop()
        self.PandaTurn.pause()

    def setMusicBoxVolume(self):
        # Cukup baca nilai saat ini dari penggeser dan atur di
        # suara
        newVol = self.slider.guiItem.getValue()
        self.musicBoxSound.setVolume(newVol)

    def toggleMusicBox(self):

        if self.boxOpen:
            self.lidOpen.pause()

            self.lidClose.start()  # Mulai interval kotak tutup
            self.PandaTurn.pause() # Jeda putaran patung
            # Simpan waktu musik saat ini
            self.musicTime = self.musicBoxSound.getTime()
            self.musicBoxSound.stop()  # Hentikan musiknya
            self.button['text'] = "Open"  # Bersiaplah untuk mengubah label tombol
        else:
            self.lidClose.pause()

            self.lidOpen.start()  # Mulai interval kotak terbuka
            self.PandaTurn.resume()  # Lanjutkan putaran menghitung
            # Atur ulang waktu musik sehingga dimulai dari yang terakhir
            self.musicBoxSound.setTime(self.musicTime)
            self.musicBoxSound.play()  # Mainkan musiknya
            self.button['text'] = "Close"  # Bersiaplah untuk mengubah close

        self.button.setText()  
        # Atur status kita menjadi kebalikan dari sebelumnya
        self.boxOpen = not self.boxOpen
# (tertutup untuk membuka atau terbuka untuk ditutup)

# Runnnnn
mb = MusicBox()
base.run()

