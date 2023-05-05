import numpy as np 
import cv2
from skimage.measure import EllipseModel
import exceptions
from scipy import optimize
#from numba import njit

class ransac:
    def __init__(self, mask, iterations, threshold):
        self.mask = mask
        self.iterations = iterations
        self.threshold = threshold
        self.points_contour = None
        
    def set_mask(self, contour):
        self.contour = contour

    def get_mask(self):
        return self.mask

    def set_iterations(self, iterations):
        self.iterations = iterations

    def get_iterations(self):
        return self.iterations

    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_threshold(self):
        return self.threshold
    
    def set_points_contour(self, points_contour):
        self.points_contour = points_contour
 
    def get_points_contour(self):
        return self.points_contour
    

    
    # Convert mask into points (contour)    
    def init_points_contour(self):
        mask = self.get_mask()
        
        if mask is None:
            raise exceptions.EmptyImageError("Mask for init_points_contour is empty")

        contour, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        if len(contour[0]) == 0 or contour is None:
            raise exceptions.EmptyImageError("Contour for init_points_contour is empty")
        
        self.set_points_contour(np.squeeze(contour[0],axis=1))
        #print (f'contour: {contour[0]}')
        return True 
    
    #Calculate the area of the ellipse
    def calc_area(self, params):
        return np.pi * params[1][0] * params[1][1]
    


    
    def fit(self):
        best_inliers = np.empty((0, 2), dtype=np.int32)


        best_ellipse = None
        best_area = 0
        ellipse_fit = EllipseModel()
        points = np.array(self.get_points_contour())
        threshold = self.get_threshold()
        #print(f'points.shape: {points.shape}')
        #print(f'points[0]: {points[0]}')
        #print(f'points[0].shape: {points[0].shape}')

        for i in range (self.get_iterations()):
            # Select 5 random points from the contour
            idx = np.random.choice(len(points), 5, replace = False)
            #print(f'i: {i} idx: {idx}')
            # Fit an ellipse to the selected points
            #print(f'points[idx,:]: {points[idx,:]}')
            #print(f'points[idx,:].shape: {points[idx,:].shape}')
            #if not ellipse_fit.estimate(np.flip(points[idx,:])):
            #   continue
            params = cv2.fitEllipse(points[idx,:])
            #print(f'get_params: {params}')
            if params is None:
                continue
            #print(f'params: {params}')

            #plot_points_and_circle(params,points[idx,:])

            area = self.calc_area(params)
            #print(f'points: {points}, params: {params}, threshold: {threshold}, area: {area}, best_area: {best_area}')
            best_ellipse, best_inliers, best_area = evaluate(points, params, threshold, area, best_area, best_inliers,best_ellipse, points[idx,:])

            
        return best_ellipse, best_inliers, best_area

    def ransac_start(self):
        self.init_points_contour()
        best_ellipse, best_inliers, best_area = self.fit()
        
        center, axis, theta = best_ellipse
        x,y = center
        a,b = axis
        x = round(x)
        y= round(y)
        a = round(a)
        b = round(b)
    
        e = (x,y,a,b,theta)
        return e, best_inliers, best_area
    
    
    
def plot_points_and_circle(params,pointfit):
            
    mask_eval = np.zeros((200,200),dtype = np.uint8)
    mask_eval = cv2.cvtColor(mask_eval, cv2.COLOR_GRAY2BGR)
    mask_eval = cv2.ellipse(mask_eval, (round(params[0][1]),round(params[0][0])),(round(params[1][0]/2),round(params[1][1]/2)),round(params[2]),0,360,(0,255,0),1)
    mask_eval = cv2.ellipse(mask_eval,(100,100),(50,25),20,0,360,(255,0,0),1)
    for p in pointfit: 
        mask_eval = cv2.circle(mask_eval,(p[0],p[1]),1, (0,255,255), 2)
    cv2.imshow('mask_eval',mask_eval)
    key = cv2.waitKey(1)

    if key == ord('q'):  # Press 'q' to exit
        cv2.destroyAllWindows()

#@njit(nogil=True)
def distance(point, params,threshold):
    #x, y = point
    #xc, yc, a, b, theta = params
    #
    #A = (a**2) * (np.sin(theta)**2) + (b**2) * (np.cos(theta)**2)
    #B = 2 * (b**2 - a**2) * np.sin(theta) * np.cos(theta)
    #C = (a**2) * (np.cos(theta)**2) + (b**2) * (np.sin(theta)**2)
    #D = -2 * A * xc - B * yc
    #E = -2 * C * yc - B * xc
    #F = A * xc**2 + B * xc * yc + C * yc**2 - a**2 * b**2
    #
    #ellipse_val = A * x**2 + B * x * y + C * y**2 + D * x + E * y + F
    #print(f'ellipse_val: {ellipse_val}')
#
    # # Compute the distance between the point and the center of the ellipse
    #print(f'dist_to_center: {dist_to_center}')
#   # # Find the closest point on the ellipse boundary to the given point
    #
    ## Compute the distance between the closest point on the boundary and the center of the ellipse
#
#   # # Check if the point is inside the ellipse
    #if np.abs(ellipse_val) <= threshold:
    #    return True
    #elif dist_to_center < 1 
    # True
    #else:
    #    return 10
       # Unpack the ellipse parameters
    pass
    
    
def boundary_dist(phi, point, params):
    #print(f'point boundary dist: {point}')
    #print(f'params boundary dist: {params}')
    #print(f'phi boundary dist: {phi}')
    center, axis, angle = params
    xc, yc = center
    a, b = axis
    #coordination transformation 
    #new center
    #print(f'xr: {xr}')
    #print(f'yc: {yc}')
    
    #rotate over new center 
    x0 =xc + a * np.cos(angle) * np.cos(phi) - b * np.sin(angle) * np.sin(phi)
    y0 =yc + a * np.sin(angle) * np.cos(phi) + b * np.cos(angle) * np.sin(phi)
    #print(f'x0: {x0}')
    return  (point[0]-x0)**2 + (point[1]-y0)**2


def dist_boundary(point, params, threshold):
    center, axis, angle = params
    xc, yc = center
    a, b = axis
    phi = np.arctan2(point[1]-yc, point[0]-xc)
    #print(f'phi: {phi}')
    phi_o, _ = optimize.leastsq(boundary_dist,phi, args=(point,params))
    #print(f'phi_o: {phi_o}')
    distance = boundary_dist(phi_o,point, params)
    #print(f'distance: {distance}')
    
    if distance < threshold:
        return 0
    elif distance < 1:
        return 0

    else :
        return 10


#@njit(nogil=True)
def evaluate(points, params, threshold, area, best_area, best_inliers, best_ellipse, pointfit):

    # Find the inliers
    #print(f'points: {points}, params: {params}, threshold: {threshold}, area: {area}, best_area: {best_area}')
    inliers = np.zeros((0, 2), dtype=np.int32)     # initialize best_inliers to an empty numpy array
    for point in points:
        dist = dist_boundary(point, params, threshold)
        if dist < threshold:
            inliers = np.vstack((inliers,  point))
                     
    if inliers.shape[0] > best_inliers.shape[0]:
        best_inliers =inliers
        best_ellipse = params
        best_area = area
    return best_ellipse, best_inliers, best_area


if __name__ == '__main__':
    mask = np.zeros((200,200),dtype = np.uint8)
    #mask = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
    mask = cv2.ellipse(mask,(100,100),(50,25),20,0,360,(255,0,0),1)
    cv2.imshow('mask',mask)
    
    rans = ransac(mask, 150 ,0.001 )
    a,b,c = rans.ransac_start()
    print(f'best_ellipse: {a} best_inliers: {b} best_area: {c}')
    print(f'lenght of best_inliers: {len(b)}')
    print(f'leng points_contour: {len(rans.get_points_contour())}')
    test = np.zeros((200,200),dtype = np.uint8)
    mask = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)

    mask = cv2.ellipse(mask, (a[0],a[1]), (round(a[2]/2),round(a[3]/2)), a[4],0,360,(0,255,0),1)
    cv2.imshow('test',mask)
    cv2.waitKey(0)