import numpy as np 
import cv2 
import pandas as pd

class pupil: 
    """This class is used to process images of eyes to find the center and outline of the pupils aswell of the iris 
    """
    def __init__(self, path=None, gray=None, ):
        self._path = path
        self._center = np.array([0,0])
        self._radius = 0
        self._img = None
        self._gray = None
        self._processing = gray
        self._center_iris = np.array([0,0])
        self._radius_iris = 0
        self._ROI = None
        #._ROI_coords = [x1,y1],[x2,y2]
        self._ROI_coords = np.array([[0,0],[0,0]]) 
    
    def load_image(self,visual= False):
        self._img = cv2.imread(self._path)
        self._processing = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)
        self._gray=self._processing.copy()
        if visual:
            self.visual_picture()

    def visual_picture(self, img=None):
        """use opencv to show images

        Args:
            img (np.array, optional): shows this image instead of self._processing Defaults to None.
        """

        cv2.imshow("original", self._img)
        if img is None:
            cv2.imshow("processed", self._processing)
        else: 
            cv2.imshow("processed", img)

        key = cv2.waitKey(0)
        if key == 27:
            cv2.destroyAllWindows()
            
    def set_img(self,img):
        self._img = img
        
    def get_img(self):
        return self._img
        
    def set_gray(self, img):
        self._gray = img
    
    def preprocess_image(self, g_b_Kernel=(3, 3), sig_x=0, visual= False,):
        """Uses Gaussian blur on class pupil_detection and saves it in _processing

        Args:
            g_b_Kernel (tuple, optional): kernel size of Gaussian Blur (must be uneven). Defaults to (3, 3).
            sig_x (int, optional): sigmaX. Defaults to 0.
            visual (bool, optional): show results. Defaults to False.
        """
        img = cv2.GaussianBlur(self._gray, g_b_Kernel, sig_x)
        self._processing = img
        if visual:
            self.visual_picture()
        
    def canny(self, th1=5, th2=70, edge=3, visual = False):
        self._processing = cv2.Canny(self._processing, th1, th2, edge)
        
        if visual:
            self.visual_picture()
        
    def hough_circle(self, dp=2, mindist=80, p1=30, p2=50, r_min=0, r_max=30, visual= False):
        circles = cv2.HoughCircles(self._processing, cv2.HOUGH_GRADIENT, dp, minDist=mindist,
                                   param1=p1, param2=p2, minRadius=r_min,maxRadius=r_max)
        """uses hough_circles on the instance pupile_detection
        extracts radius and center from the circles found and saves them in class properties
        """
        
        if visual:
            img_0 = self._img.copy()
            
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            if self._radius: 
                for (x,y,r) in circles:
                    
                    if ((x - self._center[0])**2 + (y - self._center[1])**2 < ( (self._radius/9)**2)):
                        
                        self._center_iris = np.array([x,y])
                        self._radius_iris = r
                        
                        if visual: 
                            cv2.circle(img_0, (x,y),0,(0,0,255),6)
                            cv2.circle(img_0,(x,y),r,(0,0,255),2)
                         
            for (x,y,r) in circles:
                #Save information 
                self._center = np.array([x,y])
                self._radius = r
                
                # visualize circles in relation to the original image
                if visual:
                    cv2.circle  (img_0, (x, y), 0, (0, 255, 0), 6)
                    cv2.circle(img_0, (x, y), r, (0, 0, 255), 1)
                    
            if visual: self.visual_picture(img_0)
    
    def extract_ROI(self, center, radius, visual=False):
        """extracts a region of interest in the original image based on center and radius 

        Args:
            center (np.array): information x,y
            radius (integer): radius of the pupil
            visual (bool, optional): visualize results. Defaults to False.

        Returns:
            _type_: _description_
        """
        print(center,radius)
        print('x1 of new area',center[0]-radius, 'y1 of new area',center[0]+radius,'x2 of new area',center[1]-radius,'y2 of new area',center[1]+radius)
        self._ROI= self._img[center[1]-3*radius:center[1]+3*radius,center[0]-3*radius:center[0]+3*radius] 
     
        if visual: 
            self.visual_picture(self._ROI)
        return self._ROI        
            
            
            
if __name__ == '__main__':
    # lad images  
    #create instance of pupil
    
    pupil_test = pupil('test.jpg')
    
    # Load and preprocess image
    pupil_test.load_image()
    imgx = cv2.Sobel(pupil_test.get_img(), cv2.CV_64F, 1, 0, ksize=5)
    imgy = cv2.Sobel(pupil_test.get_img(), cv2.CV_64F, 0, 1, ksize=5)
    mag = np.hypot(imgx, imgy)
    orientation = np.arctan2(imgy, imgx)*180/np.pi +180
    
    pupil_test.preprocess_image((15,15), 5,visual=False)
    
    # use canny and hough circle to find center and radius of the pupil
    pupil_test.canny(visual=True, th1=35,th2=40)
    pupil_test.hough_circle(visual=True, dp=2, r_max= 30, r_min=10)
    
    
    # get radius of the pupil
    radius = pupil_test._radius
    center = pupil_test._center
    try:
        region = pupil_test.extract_ROI(center, radius, visual=True)
        
    except:
        print('no center, no radius was found')
        
    # preprocess image differently to achieve higher accuracy on the iris
    ROI = region.copy()
    cv2.GaussianBlur(ROI, (15,15),5)
    ROI = cv2.Canny(ROI,50,60,2 ) 
    cv2.imshow("ROI", ROI)
    cv2.waitKey(0)
    
    circles = cv2.HoughCircles(ROI, cv2.HOUGH_GRADIENT,dp = 2,minDist=50 ,param1=40, param2=100,maxRadius=int(radius*3), minRadius= int(radius*1.5))
    if circles is not None:
        
        circles = np.round(circles[0, :]).astype("int")
        for (x,y,r) in circles:
                
                #if ((x - self._center[0])**2 + (y - self._center[1])**2 < ( (self._radius/9)**2)):
                    
                     
            cv2.circle(region, (x,y),0,(0,0,255),4)
            cv2.circle(region,(x,y),r,(0,0,255),1)
            cv2.imshow("region",region)
            cv2.waitKey(0)
    
    #pupil_test.preprocess_image((9,9), 10,visual=False)
    #pupil_test.canny(20,30, visual=True)
    
    
    # detect irlis, use the radius of the pupil to calculate the min and max radius 
    # average diameter pupil = 2-9 mm 12/9, 12/2
    # average diameter iris = 12 mm 
    
    #pupil_test.hough_circle(visual=False, dp=2, r_max=int(radius*3),r_min=int(radius*(11/9)))

                                