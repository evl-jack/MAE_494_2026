"""Small-case numerical checks; these do not change the report experiment."""
import unittest
import numpy as np
from deblur_report import (make_gaussian_transfer, apply_blur_rgb,
                          spectral_deblur_rgb, relative_gradient, exact_gd_stop,
                          cg_channel, resize_bicubic)


class DeblurChecks(unittest.TestCase):
    def test_small_hessian_against_explicit_matrix(self):
        psf, Hf = make_gaussian_transfer(2,2,.5)
        A = np.column_stack([apply_blur_rgb(np.eye(4)[:,j].reshape(2,2,1),Hf).ravel() for j in range(4)])
        H = A.T@A + 1e-4*np.eye(4)
        np.testing.assert_allclose(np.linalg.eigvalsh(H),np.sort((np.abs(Hf)**2+1e-4).ravel()),atol=1e-14)
        np.testing.assert_allclose(np.diag(H),np.sum(psf**2)+1e-4,atol=1e-14)
        # Hand calculation: normalized two-tap Gaussian [1, exp(-2)].
        expected=np.array([1,((1-np.exp(-2))/(1+np.exp(-2)))**2,
                             ((1-np.exp(-2))/(1+np.exp(-2)))**2,
                             ((1-np.exp(-2))/(1+np.exp(-2)))**4])+1e-4
        np.testing.assert_allclose(np.linalg.eigvalsh(H),np.sort(expected),atol=1e-14)

    def test_fourier_gd_matches_explicit_steps(self):
        _,Hf=make_gaussian_transfer(4,6,.7)
        b=np.random.default_rng(1).normal(size=(4,6,3))
        h=np.abs(Hf)**2+1e-4
        alpha=2/(h.max()+h.min())
        rhs=Hf.conj()[:,:,None]*np.fft.fft2(b,axes=(0,1))
        energy=np.sum(np.abs(rhs)**2,axis=2)
        x=np.zeros_like(b)
        initial=np.fft.ifft2(rhs,axes=(0,1)).real
        for k in range(8):
            grad=apply_blur_rgb(apply_blur_rgb(x,Hf)-b,Hf.conj())+1e-4*x
            actual=np.linalg.norm(grad)/np.linalg.norm(initial)
            self.assertAlmostEqual(actual,relative_gradient(energy,np.abs(1-alpha*h),k),places=12)
            x-=alpha*grad

    def test_cg_and_direct_solution(self):
        _,Hf=make_gaussian_transfer(4,6,.7)
        b=np.random.default_rng(1).normal(size=(4,6,3))
        direct=spectral_deblur_rgb(b,Hf,1e-4)
        for c in range(3):
            rhs=Hf.conj()*np.fft.fft2(b[:,:,c])
            x,info,residual,_=cg_channel(np.abs(Hf)**2+1e-4,rhs,1e-12,500)
            self.assertEqual(info,0)
            self.assertLess(residual,1e-12)
            np.testing.assert_allclose(np.fft.ifft2(x).real,direct[:,:,c],atol=1e-9)

    def test_exact_stop_and_zero_input(self):
        k,ok=exact_gd_stop(np.ones((1,1)),np.array([[.5]]),.1,20)
        self.assertEqual((k,ok),(4,True))
        self.assertEqual(exact_gd_stop(np.ones((1,1)),np.array([[.5]]),.1,2),(2,False))
        self.assertEqual(exact_gd_stop(np.zeros((1,1)),np.array([[.5]]),.1,20),(0,True))

    def test_resize_identity_and_constant(self):
        x=np.random.default_rng(1).random((5,7,3))
        np.testing.assert_allclose(resize_bicubic(x,(5,7)),x,atol=1e-14)
        np.testing.assert_allclose(resize_bicubic(np.ones((5,7,3)),(9,4)),1,atol=1e-14)


if __name__=='__main__':
    unittest.main()
