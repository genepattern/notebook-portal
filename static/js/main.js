/**
 * Import the application module
 */
import * as GenePattern from "/static/js/app.js";
window.GenePattern = GenePattern;

/**
 * Code to run when the document is ready
 */
$(document).ready(function() {
    // Init smooth scrolling
    const scroll = new SmoothScroll('a[href*="#"]');

    // Check the size of the header at load
    if ($(document).scrollTop() > 50) {
        $('header').addClass('shrink');
    }

    // Adjust the size of the header when scrolling
    $(window).scroll(function() {
        if ($(document).scrollTop() > 50) {
            $('header').addClass('shrink');
        }
        else {
            $('header').removeClass('shrink');
        }
    });
});


