%% ================================================================
% PROJECT 2 - ILL-CONDITIONED IMAGE DEBLURRING
%
% Uses a 2K COLOR image.
%
% Optimization problem:
%
%   minimize_x  1/2 ||A*x - b||^2 + lambda/2 ||x||^2
%
% where:
%   x = original/deblurred image
%   A = Gaussian blur operator
%   b = blurry/noisy image
%
% Hessian:
%
%   H = A'*A + lambda*I
%
% Demonstrates:
%   D1 - Hessian eigenvalue spectrum / condition number
%   D2 - Intrinsic ill-conditioning + Jacobi scaling
%   D3 - Gradient Descent convergence
%   D4 - Conjugate Gradient convergence
%
% Final output:
%   Full 2048-pixel-wide RGB deblurred image
%
% ================================================================

clear;
close all;
clc;

rng(1);


%% ================================================================
% 1. LOAD THE STADIUM IMAGE
% ================================================================

imageFile = 'stadium.png';

% If stadium.png is not in the MATLAB Current Folder,
% ask the user to select the image.
if ~isfile(imageFile)

    [fileName, pathName] = uigetfile( ...
        {'*.png;*.jpg;*.jpeg', 'Image Files (*.png, *.jpg, *.jpeg)'}, ...
        'Select Stadium Image');

    if isequal(fileName,0)
        error('No image was selected.');
    end

    imageFile = fullfile(pathName,fileName);

end


% Read image
img = imread(imageFile);

% Convert to double precision [0,1]
img = im2double(img);


% If grayscale, convert to RGB
if ndims(img) == 2
    img = repmat(img,1,1,3);
end

% If image contains extra channels, keep RGB only
if size(img,3) > 3
    img = img(:,:,1:3);
end


fprintf('\nImage loaded from:\n%s\n\n',imageFile);


%% ================================================================
% 2. RESIZE TO 2K
% ================================================================

% 2K width
targetWidth = 2048;

originalHeight = size(img,1);
originalWidth  = size(img,2);

scale = targetWidth/originalWidth;

targetHeight = round(originalHeight*scale);


% Preserve aspect ratio
xTrue2K = imresize( ...
    img, ...
    [targetHeight targetWidth], ...
    'bicubic');


[nRows2K,nCols2K,nChannels] = size(xTrue2K);


fprintf('2K image dimensions:\n');
fprintf('%d x %d x %d\n\n', ...
    nCols2K,nRows2K,nChannels);


%% ================================================================
% 3. MAIN DEBLURRING PARAMETERS
% ================================================================

% Gaussian blur radius in pixels
sigma2K = 6.0;

% Tikhonov regularization
lambda = 1e-4;

% Noise level
noiseStd = 0.001;


fprintf('Blur sigma = %.2f pixels\n',sigma2K);
fprintf('Regularization lambda = %.2e\n',lambda);
fprintf('Noise standard deviation = %.4f\n\n',noiseStd);


%% ================================================================
% 4. CREATE 2K GAUSSIAN BLUR OPERATOR
% ================================================================

[psf2K,Hf2K] = makeGaussianTransfer( ...
    nRows2K, ...
    nCols2K, ...
    sigma2K);


%% ================================================================
% 5. CREATE BLURRED + NOISY 2K IMAGE
% ================================================================

bClean2K = applyBlurRGB(xTrue2K,Hf2K);

noise = noiseStd*randn(size(bClean2K));

b2K = bClean2K + noise;

% Keep valid RGB range for display
bDisplay2K = clampImage(b2K);


%% ================================================================
% 6. FULL 2K DIRECT FOURIER DEBLURRING
% ================================================================
%
% Solve:
%
% (A'*A + lambda*I)x = A'*b
%
% Gaussian convolution is diagonal in Fourier space.
%
% Therefore:
%
% X = conj(Hf).*Bf / (|Hf|^2 + lambda)

tic;

xDeblur2K = spectralDeblurRGB( ...
    b2K, ...
    Hf2K, ...
    lambda);

directSolveTime = toc;

xDeblurDisplay2K = clampImage(xDeblur2K);


fprintf('Full 2K Fourier deblurring time: %.3f seconds\n\n', ...
    directSolveTime);


%% ================================================================
% 7. DISPLAY FULL 2K RESULT
% ================================================================

figure('Name','2K Stadium Deblurring');

subplot(1,3,1);

imshow(xTrue2K);

title('Original 2K Image');


subplot(1,3,2);

imshow(bDisplay2K);

title(sprintf('Blurred + Noise, \\sigma = %.1f',sigma2K));


subplot(1,3,3);

imshow(xDeblurDisplay2K);

title('Deblurred 2K Image');


sgtitle('2K Color Image Deblurring');



%% ================================================================
% IMPORTANT:
%
% For iterative optimization diagnostics, use a smaller version.
%
% The final image above is TRUE 2K.
%
% Running thousands of GD iterations directly on an
% 8-million-variable RGB image is unnecessarily expensive.
%
% The smaller version has the SAME optimization structure and
% illustrates the conditioning much faster.
%
% Change analysisWidth to 2048 if you want everything done at 2K.
% ================================================================

analysisWidth = 1080;

analysisScale = analysisWidth/nCols2K;

analysisHeight = round(nRows2K*analysisScale);


xTrue = imresize( ...
    xTrue2K, ...
    [analysisHeight analysisWidth]);


[nRows,nCols,~] = size(xTrue);


% Scale Gaussian blur proportionally
sigma = sigma2K*analysisScale;


fprintf('============================================\n');
fprintf('OPTIMIZATION ANALYSIS IMAGE\n');
fprintf('============================================\n');

fprintf('Analysis resolution: %d x %d RGB\n', ...
    nCols,nRows);

fprintf('Equivalent sigma: %.3f pixels\n\n',sigma);


%% ================================================================
% 9. CREATE ANALYSIS BLUR OPERATOR
% ================================================================

[psf,Hf] = makeGaussianTransfer( ...
    nRows, ...
    nCols, ...
    sigma);


%% ================================================================
% 10. CREATE ANALYSIS BLURRED IMAGE
% ================================================================

bClean = applyBlurRGB(xTrue,Hf);

b = bClean + noiseStd*randn(size(bClean));


%% ================================================================
% D1 - HESSIAN CONDITION NUMBER
% ================================================================
%
% Hessian:
%
%   H = A'*A + lambda*I
%
% Fourier eigenvalues:
%
%   eig(H) = |Hf|^2 + lambda

eigH = abs(Hf).^2 + lambda;


lambdaMin = min(eigH(:));
lambdaMax = max(eigH(:));

kappa = lambdaMax/lambdaMin;


fprintf('============================================\n');
fprintf('D1 - HESSIAN CONDITION NUMBER\n');
fprintf('============================================\n');

fprintf('Minimum eigenvalue = %.6e\n',lambdaMin);
fprintf('Maximum eigenvalue = %.6e\n',lambdaMax);
fprintf('Condition number    = %.6e\n\n',kappa);


%% ================================================================
% D1 FIGURE - EIGENVALUE SPECTRUM
% ================================================================

eigSorted = sort(eigH(:));


% Plot a sample instead of every eigenvalue
numberOfPlotPoints = min(10000,numel(eigSorted));

plotIndices = round( ...
    linspace(1,numel(eigSorted),numberOfPlotPoints));


figure('Name','Hessian Spectrum');

semilogy( ...
    plotIndices, ...
    eigSorted(plotIndices), ...
    '.', ...
    'MarkerSize',7);

xlabel('Eigenvalue Index');

ylabel('\lambda_i');

title(sprintf( ...
    'Hessian Eigenvalue Spectrum, \\kappa = %.2e', ...
    kappa));

grid on;


%% ================================================================
% D2 - INTRINSIC ILL-CONDITIONING
% ================================================================
%
% Increase Gaussian blur sigma.
%
% More blur destroys more high-frequency information.
%
% This causes small eigenvalues of A'*A and increases kappa.
%
% Jacobi scaling does not fix the conditioning because the diagonal
% of the circular convolution Hessian is constant.

sigmaList = [ ...
    0.35 ...
    0.50 ...
    0.70 ...
    1.00 ...
    1.30 ...
    1.60 ...
    2.00];


kappaOriginal = zeros(size(sigmaList));
kappaJacobi   = zeros(size(sigmaList));


for i = 1:length(sigmaList)

    sigma_i = sigmaList(i);


    [psf_i,Hf_i] = makeGaussianTransfer( ...
        nRows, ...
        nCols, ...
        sigma_i);


    eigHi = abs(Hf_i).^2 + lambda;


    % Original Hessian
    kappaOriginal(i) = ...
        max(eigHi(:))/min(eigHi(:));


    % ------------------------------------------------------------
    % Jacobi scaling
    %
    % diag(H) is constant for periodic convolution:
    %
    % diag(H) =
    % sum(psf.^2) + lambda
    %
    % Therefore the scaled Hessian only differs from H by a scalar.
    % ------------------------------------------------------------

    diagH = sum(psf_i(:).^2) + lambda;


    eigScaled = eigHi/diagH;


    kappaJacobi(i) = ...
        max(eigScaled(:))/min(eigScaled(:));

end


fprintf('============================================\n');
fprintf('D2 - INTRINSIC CONDITIONING TEST\n');
fprintf('============================================\n');

fprintf(' sigma       kappa(H)       kappa(Jacobi)\n');
fprintf('---------------------------------------------\n');


for i = 1:length(sigmaList)

    fprintf('%6.2f    %12.3e    %12.3e\n', ...
        sigmaList(i), ...
        kappaOriginal(i), ...
        kappaJacobi(i));

end


fprintf('\n');


%% ================================================================
% D2 FIGURE
% ================================================================

figure('Name','Condition Number vs Blur');

semilogy( ...
    sigmaList, ...
    kappaOriginal, ...
    'o-', ...
    'LineWidth',1.5, ...
    'MarkerSize',7);

hold on;

semilogy( ...
    sigmaList, ...
    kappaJacobi, ...
    's--', ...
    'LineWidth',1.5, ...
    'MarkerSize',7);


xlabel('Gaussian Blur Strength \sigma');

ylabel('Condition Number \kappa');

title('Intrinsic Ill-Conditioning');

legend( ...
    'Original Hessian', ...
    'After Jacobi Scaling', ...
    'Location','northwest');

grid on;


%% ================================================================
% D3 - GRADIENT DESCENT
% ================================================================
%
% Objective:
%
% f(x) = 1/2 ||Ax-b||^2 + lambda/2 ||x||^2
%
% Gradient:
%
% grad f =
%
% A'*(Ax-b) + lambda*x
%
%
% For this quadratic, the best constant GD step size is:
%
% alpha = 2 / (lambda_max + lambda_min)

alpha = 2/(lambdaMax + lambdaMin);


fprintf('============================================\n');
fprintf('D3 - GRADIENT DESCENT\n');
fprintf('============================================\n');

fprintf('GD step size = %.6e\n',alpha);


%% ================================================================
% COMPUTE FOURIER DATA FOR GD
% ================================================================
%
% Because Fourier transform diagonalizes the Hessian,
% we can calculate the exact GD trajectory efficiently.
%
% This is mathematically the SAME gradient descent algorithm.

hEig = abs(Hf).^2 + lambda;

rho = 1 - alpha*hEig;


% Energy of the initial gradient
rhsEnergy = zeros(nRows,nCols);


for c = 1:3

    Bf = fft2(b(:,:,c));

    rhsF = conj(Hf).*Bf;

    rhsEnergy = ...
        rhsEnergy + abs(rhsF).^2;

end


initialGradientEnergy = sum(rhsEnergy(:));


%% ================================================================
% GRADIENT DESCENT CONVERGENCE HISTORY
% ================================================================

maxGDIterations = 20000;

% Sample iteration numbers logarithmically.
%
% This avoids calculating all 20,000 iterations while still showing
% the exact convergence curve.

iterationSamples = unique([ ...
    0, ...
    round(logspace(0,log10(maxGDIterations),300)), ...
    maxGDIterations]);


relativeGradientGD = zeros(size(iterationSamples));


absRho = abs(rho);


for j = 1:length(iterationSamples)

    k = iterationSamples(j);

    factor = absRho.^(2*k);

    currentGradientEnergy = ...
        sum(rhsEnergy(:).*factor(:));


    relativeGradientGD(j) = ...
        sqrt(currentGradientEnergy/initialGradientEnergy);

end


%% Find approximate GD stopping iteration

gdTolerance = 1e-4;


firstGDConverged = ...
    find(relativeGradientGD < gdTolerance,1);


if isempty(firstGDConverged)

    gdIterations = maxGDIterations;

    fprintf('GD did NOT reach %.1e in %d iterations.\n', ...
        gdTolerance,maxGDIterations);

else

    gdIterations = ...
        iterationSamples(firstGDConverged);

    fprintf('GD reaches %.1e at approximately %d iterations.\n', ...
        gdTolerance,gdIterations);

end


%% ================================================================
% RECONSTRUCT THE GD IMAGE
% ================================================================

xGD = zeros(size(xTrue));


gdFactor = 1 - rho.^gdIterations;


for c = 1:3

    Bf = fft2(b(:,:,c));


    rhsF = conj(Hf).*Bf;


    XstarF = rhsF./hEig;


    XgdF = XstarF.*gdFactor;


    xGD(:,:,c) = real(ifft2(XgdF));

end


xGDDisplay = clampImage(xGD);


%% ================================================================
% D4 - CONJUGATE GRADIENT
% ================================================================
%
% Solve:
%
% Hx = A'b
%
% using Conjugate Gradient.
%
% We solve it in the Fourier basis.
%
% The problem is mathematically equivalent, but the Hessian becomes
% diagonal, making matrix-vector multiplication very inexpensive.

fprintf('\n============================================\n');
fprintf('D4 - CONJUGATE GRADIENT\n');
fprintf('============================================\n');


cgTolerance = 1e-4;

maxCGIterations = 500;


xCG = zeros(size(xTrue));


hVector = hEig(:);


cgIterationsEachChannel = zeros(3,1);


cgHistory = [];


for c = 1:3

    Bf = fft2(b(:,:,c));

    rhsF = conj(Hf).*Bf;


    rhsVector = rhsF(:);


    % Hessian multiplication in Fourier space
    Hmult = @(z) hVector.*z;


    [XcgVector,flag,relres,iterationsCG,resvec] = ...
        pcg( ...
            Hmult, ...
            rhsVector, ...
            cgTolerance, ...
            maxCGIterations);


    XcgF = reshape( ...
        XcgVector, ...
        nRows, ...
        nCols);


    xCG(:,:,c) = real(ifft2(XcgF));


    cgIterationsEachChannel(c) = iterationsCG;


    fprintf('\nChannel %d:\n',c);
    fprintf('  CG iterations = %d\n',iterationsCG);
    fprintf('  Relative residual = %.3e\n',relres);
    fprintf('  PCG flag = %d\n',flag);


    % Save first-channel history for convergence plot
    if c == 1

        cgHistory = resvec/resvec(1);

    end

end


xCGDisplay = clampImage(xCG);


maxCGUsed = max(cgIterationsEachChannel);


fprintf('\nMaximum CG iterations = %d\n\n', ...
    maxCGUsed);


%% ================================================================
% D3 / D4 CONVERGENCE COMPARISON
% ================================================================

figure('Name','GD vs CG Convergence');


semilogy( ...
    iterationSamples, ...
    relativeGradientGD, ...
    'LineWidth',1.7);

hold on;


semilogy( ...
    0:length(cgHistory)-1, ...
    cgHistory, ...
    'LineWidth',1.7);


xlabel('Iteration');

ylabel('Relative Gradient / Residual');

title('Gradient Descent vs Conjugate Gradient');

legend( ...
    'Gradient Descent', ...
    'Conjugate Gradient', ...
    'Location','southwest');

grid on;


%% ================================================================
% DISPLAY OPTIMIZATION RESULTS
% ================================================================

figure('Name','Optimization Results');


subplot(2,2,1);

imshow(xTrue);

title('Original');


subplot(2,2,2);

imshow(clampImage(b));

title('Blurred + Noise');


subplot(2,2,3);

imshow(xGDDisplay);

title(sprintf( ...
    'Gradient Descent, %d iterations', ...
    gdIterations));


subplot(2,2,4);

imshow(xCGDisplay);

title(sprintf( ...
    'Conjugate Gradient, max %d iterations', ...
    maxCGUsed));


sgtitle('Ill-Conditioned Image Deblurring');


%% ================================================================
% RECONSTRUCTION ERRORS
% ================================================================

errorBlur = ...
    norm(clampImage(b(:)) - xTrue(:)) ...
    / norm(xTrue(:));


errorGD = ...
    norm(xGDDisplay(:)-xTrue(:)) ...
    / norm(xTrue(:));


errorCG = ...
    norm(xCGDisplay(:)-xTrue(:)) ...
    / norm(xTrue(:));


error2K = ...
    norm(xDeblurDisplay2K(:)-xTrue2K(:)) ...
    / norm(xTrue2K(:));


fprintf('============================================\n');
fprintf('FINAL RESULTS\n');
fprintf('============================================\n');

fprintf('Condition number       = %.3e\n',kappa);

fprintf('Blurred image error    = %.5f\n',errorBlur);

fprintf('GD reconstruction error = %.5f\n',errorGD);

fprintf('CG reconstruction error = %.5f\n',errorCG);

fprintf('2K reconstruction error = %.5f\n',error2K);

fprintf('GD iterations shown     = %d\n',gdIterations);

fprintf('Maximum CG iterations   = %d\n',maxCGUsed);

fprintf('2K direct solve time     = %.3f seconds\n', ...
    directSolveTime);


%% ================================================================
% FINAL 2K COMPARISON FIGURE
% ================================================================

figure('Name','Final 2K Comparison');


subplot(2,1,1);

imshow(bDisplay2K);

title('Blurred 2K Color Image');


subplot(2,1,2);

imshow(xDeblurDisplay2K);

title('Deblurred 2K Color Image');


sgtitle('Final 2K Stadium Reconstruction');


%% ================================================================
% LOCAL FUNCTION:
% GAUSSIAN BLUR TRANSFER FUNCTION
% ================================================================

function [psf,Hf] = makeGaussianTransfer( ...
    nRows,nCols,sigma)

    % Pixel coordinates
    y = -floor(nRows/2):(ceil(nRows/2)-1);

    x = -floor(nCols/2):(ceil(nCols/2)-1);


    [X,Y] = meshgrid(x,y);


    % Gaussian point spread function
    psf = exp( ...
        -(X.^2 + Y.^2)/(2*sigma^2));


    % Normalize blur kernel
    psf = psf/sum(psf(:));


    % Move center to FFT origin
    psfShifted = ifftshift(psf);


    % Fourier transfer function
    Hf = fft2(psfShifted);

end


%% ================================================================
% LOCAL FUNCTION:
% APPLY RGB BLUR
% ================================================================

function y = applyBlurRGB(x,Hf)

    y = zeros(size(x));


    for c = 1:size(x,3)

        Xf = fft2(x(:,:,c));


        y(:,:,c) = real( ...
            ifft2(Hf.*Xf));

    end

end


%% ================================================================
% LOCAL FUNCTION:
% FULL SPECTRAL DEBLURRING
% ================================================================

function x = spectralDeblurRGB(b,Hf,lambda)

    x = zeros(size(b));


    denominator = ...
        abs(Hf).^2 + lambda;


    for c = 1:size(b,3)

        Bf = fft2(b(:,:,c));


        Xf = ...
            conj(Hf).*Bf ...
            ./ denominator;


        x(:,:,c) = real(ifft2(Xf));

    end

end


%% ================================================================
% LOCAL FUNCTION:
% CLAMP IMAGE TO VALID RGB VALUES
% ================================================================

function x = clampImage(x)

    x = max(0,min(1,x));

end