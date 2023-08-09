# from selenium import webdriv er
import math
from random import randint

class WindowsDriverAdmin:
    drivers = []
    # lock = Lock()
    def __init__(self, resolution=[1920, 1080], url='https://www.google.com',lock = None):
        self.url = url
        self.resolution = resolution
        self.lock = lock
    # @property
    # def safe_drivers(self):
    #     with self.lock:
    #         return self.drivers
    def add_driver(self, driver):
        # driver.get(self.url)
        if self.lock:
            with self.lock:
                if driver not in self.drivers:
                    self.drivers.append(driver)
                    self.update_windows()
        elif driver not in self.drivers:
        
            self.drivers.append(driver)
            self.update_windows()
    def remove_driver(self,driver):
        try:
            self.drivers.remove(driver)
            self.update_windows()
        except ValueError:
            return 
    def get_position(self, index, position,size,quadrants):
        
        start_x, start_y = position
        width, height = size
        if quadrants  == 1:
            position = start_x, start_y
            size = width, height

        elif quadrants == 2:
            if index == 0:
                position = start_x, start_y
                size = width/2, height
            elif index ==1:
                position = start_x+width/2, start_y
                size = width/2, height
        elif quadrants == 3:
            if index == 0:
                position = start_x, start_y
                size = width/2, height
            elif index ==1:
                position = start_x+width/2, start_y
                size = width/2, height/2
            elif index ==2:
                position = start_x+width/2, start_y+height/2
                size = width/2, height/2
        elif quadrants == 4:
            if index == 0:
                position = start_x, start_y
                size = width/2, height/2
            if index == 1:
                position = start_x, start_y+height/2
                size = width/2, height/2
            elif index ==2:
                position = start_x+width/2, start_y
                size = width/2, height/2
            elif index ==3:
                position = start_x+width/2, start_y+height/2
                size = width/2, height/2
        return position,size
    def assign_position_size(self,  index, start_x, start_y, width, height,len_drivers):
        if len_drivers <=4:

            # input(f"len less or equals than {index} - {len_drivers}")
            position, size = self.get_position(index, start_x, start_y, width, height,len_drivers)
            return position,size
        else:
            # input(f"len eagger  than {index} - {len_drivers}")


            assing_to = len_drivers%4 -1
            section_position, section_size = self.get_position(assing_to, start_x, start_y, width, height,4)
            amount_drivers_in_section = (len_drivers//4)+1
            return self.assign_position_size(assing_to,section_position[0],section_position[1],section_size[0],section_size[1],amount_drivers_in_section)
        
            

    def update_windows(self):
        _id = randint(1,10)
        len_drivers = len(self.drivers)
        print(f'--- {_id}: Driver Manager for {len_drivers} ---')
        # input(len_drivers)
        positions = self.refactor(len_drivers,(0,0),(1344,738))
        i = 1
        for  driver,(pos,size) in zip(self.drivers,positions):
            # input("calculating ",i)
            driver.set_window_position(*pos)
            driver.set_window_size(*size)
            # print(pos)
            # print(size)
            print(f'Driver {i }:')
            print(f'\tPosición: ({pos[0]}, {pos[1]})')
            print(f'\tTamaño: ({size[0]}, {size[1]})')
            i+=1
        # input(f'--- {_id}: Driver Manager End ---')
        # for  driver in  self.drivers:
        #     s = driver.get_window_size()
        #     p = driver.get_window_position()
        #     print("hola",s)
        #     print("hola",p)


    def decompose(self,n):
        '''Reparte n drivers en max 4 pantallas'''
        base = n // 4
        remainder = n % 4
        result = [base + 1]*remainder + [base]*(4 - remainder)
        return sorted(result, reverse=True)
    
    def refactor(self,len_drivers, position,size ):
        if len_drivers<=4:
            return  [self.get_position(j, position,size,len_drivers) for j in range(len_drivers)]
        
        refactor_in_4  = self.decompose(len_drivers)
        all_positions = []
        for i,m in enumerate(refactor_in_4):
            section_position, section_size = self.get_position(i, position,size,4)    
            all_positions+= self.refactor(m,section_position,section_size)
        return all_positions
    

def test_windows_driver():
    from factory.factory import CustomDriverFactory,BrowserConfig
    from time import sleep
    n_drivers = 12
    a = WindowsDriverAdmin()
    for i in range(n_drivers):
        d = CustomDriverFactory().create_driver(BrowserConfig(block_images_fonts_css=True,headless=False,use_undetected_driver=False))
        a.add_driver(d)
        d.get("https://www.google.com/")
        sleep(3)
# test_windows_driver()