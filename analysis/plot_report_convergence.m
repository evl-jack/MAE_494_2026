function plot_report_convergence(resultsFile, outputFile)
% Replot saved evidence without rerunning or changing the optimization.
results = jsondecode(fileread(resultsFile));
fig = figure('Visible','off','Color','w','Position',[100 100 1300 520]);
cleanup = onCleanup(@() close(fig));
tiledlayout(1,2,'Padding','compact');
for panel = 1:2
    nexttile;
    semilogy(results.iterationSamples,results.relativeGradientGD,'LineWidth',1.7);
    hold on;
    semilogy(0:numel(results.cgHistoryRGB)-1,results.cgHistoryRGB,'LineWidth',1.7);
    yline(results.gdTolerance,':','Tolerance','LineWidth',1.2);
    xlabel('Iteration'); ylabel('Relative RGB gradient / residual');
    grid on;
    if panel == 1
        if results.gdConverged
            title('Full GD budget: tolerance reached');
        else
            title('Full GD budget: tolerance not reached');
        end
        xlim([0 results.maxGDIterations]);
    else
        title('First 100 iterations: CG convergence');
        xlim([0 100]);
    end
    legend('GD (RGB)','CG (RGB; stopped channels held fixed)','Location','best');
end
exportgraphics(fig,outputFile,'Resolution',150);
end
