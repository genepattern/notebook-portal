// Declare server constants
export const PUBLIC_NOTEBOOK_SEVER = 'https://notebook.genepattern.org/services/sharing/';
export const GENEPATTERN_SERVER = 'https://cloud.genepattern.org/gp/';

// Declare data cache
let _public_notebooks = null;
let _shared_notebooks = null;
let _workspace_notebooks = null;
let _genepattern_modules = null;

export function display_sidebar() {
    document.querySelector('.sidebar').style.display = 'block';
}

/**
 * Retrieves the public notebooks from the cache, if possible, from the server if not
 *
 * @returns {Promise<any>}
 */
export function public_notebooks() {
    if (_public_notebooks !== null)
        return new Promise(function(resolve) {
            resolve(_public_notebooks['results']);
        });

    else
    return fetch(PUBLIC_NOTEBOOK_SEVER + 'notebooks/')
        .then(response => response.json())
        .then(function(response) {
            _public_notebooks = response;
            return response['results'];
        });
}

/**
 * Retrieves the list of GenePattern modules from cache, if possible, from the server if not
 * @returns {Promise<any>}
 */
export function genepattern_modules() {
    if (_genepattern_modules !== null)
        return new Promise(function(resolve) {
            resolve(_genepattern_modules['all_modules']);
        });

    else
    return fetch(GENEPATTERN_SERVER + 'rest/v1/tasks/all.json/', {
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(function(response) {
            _genepattern_modules = response;
            return response['all_modules'];
        });
}

export function module_categories() {
    // Ensure that the modules have been retrieved
    return genepattern_modules().then(function() {
        return new Promise(function(resolve) {
            resolve(_genepattern_modules['all_categories']);
        });
    });
}

export function dashboard(selector) {
    const dashboard_app = new Vue({
        el: selector,
        delimiters: ['[[', ']]'],
        data: {
            notebooks: [],
            modules: []
        },
        computed: {
            tutorial_notebooks() {
                const tutorials = [];
                this.notebooks.forEach(function(nb) {
                    nb.tags.forEach(function(tag) {
                        if (tag.label === "tutorial") tutorials.push(nb);
                    });
                });
                return tutorials;
            }
        },
        created() {
            GenePattern.public_notebooks().then(r => this.notebooks = r);
            GenePattern.genepattern_modules().then(r => this.modules = r);
        },
        methods: {}
    });

    return dashboard_app;
}

export function jobs(selector) {
    gp.setServer(GENEPATTERN_SERVER);
    gp.tasks({
        success: function() {
            gp.jobs({
                success: function(response) {
                    const jobs = response['items'];
                    const jobs_parent = $(selector);
                    jobs.forEach(function(job) {
                        let job_div = $("<div></div>");
                        jobs_parent.append(job_div);
                        job_div.jobResults({
                            jobNumber: parseInt(job.jobId)
                        });
                    });
                }
            });
        }
    });
}

export function run_analysis(selector, lsid) {
    gp.setServer(GENEPATTERN_SERVER);
    gp.tasks({
        success: function() {
            let task_div = $("<div></div>");
            $(selector).append(task_div);
            task_div.runTask({
                'lsid': lsid
            });
        }
    });
}

export function analyses(selector) {
    const analyses_app = new Vue({
        el: selector,
        delimiters: ['[[', ']]'],
        data: {
            modules: [],
            categories: [],
            search: ''
        },
        computed: {},
        created() {
            GenePattern.genepattern_modules().then(r => this.modules = r);
            GenePattern.module_categories().then(r => this.categories = r);
        },
        watch: {
            'search': function(event) {
                const search = this.search.trim().toLowerCase();

                // If search is blank display module categories
                if (search === '') {
                    document.querySelector(selector).querySelector('.categories').classList.remove('d-none');
                    document.querySelector(selector).querySelector('.modules').classList.add('d-none');
                }

                // Otherwise show matching modules
                else {
                    document.querySelector(selector).querySelector('.categories').classList.add('d-none');
                    document.querySelector(selector).querySelector('.modules').classList.remove('d-none');

                    const cards = document.querySelector(selector).querySelector('.modules').querySelectorAll('.mod-card');
                    cards.forEach(function(card) {
                        // Matching module
                        if (card.textContent.toLowerCase().includes(search)) card.classList.remove('d-none');

                        // Not matching module
                        else card.classList.add('d-none');
                    });
                }
            }
        }
    });

    return analyses_app;
}

/******************
 * Vue Components *
 ******************/

Vue.component('module-category', {
    delimiters: ['[[', ']]'],
    props: ['category'],
    methods: {
        'search_or_launch': function() {
            // If this is a module
            if (this.category.lsid) {
                window.open(`/analyses/${this.category.lsid}/`)
            }

            // If this is a category
            else {
                document.querySelector('.mod-search').value = this.category.name;
                this.$root.search = this.category.name;
            }
        }
    },
    mounted: function() {
        if (this.category.lsid) this.$el.classList.add('module');
        else this.$el.classList.add('category')
    },
    template: `<div class="card mod-card" v-on:click="search_or_launch">  
                    <div class="card-body"> 
                        <h8 class="card-title">[[ category.name ]]</h8> 
                        <div class="d-none">[[ category.tags ]] [[ category.categories ]] [[ category.suites ]]</div>
                        <p class="card-text">[[ category.description ]]</p>
                    </div> 
                </div>`
});

Vue.component('notebook-card', {
    delimiters: ['[[', ']]'],
    props: ['nb'],
    methods: {
        'preview': function() {
            // If this is a GenePattern module
            if (this.nb.lsid)
                window.open(`/analyses/${this.nb.lsid}/`);

            // If this is a notebook
            else if (this.nb.quality)
                window.open(`${PUBLIC_NOTEBOOK_SEVER}notebooks/${this.nb.id}/preview/`);
        }
    },
    computed: {
        img_src() {
            // If this is a GenePattern module
            if (this.nb.lsid) return "/static/images/banner.jpg";

            // Else, if this is a notebook
            else return `/thumbnail/${this.nb.id}/`;
        }
    },
    template: `<div class="card nb-card" v-on:click="preview"> 
                    <img class="card-img-top" v-bind:src="img_src" alt="Notebook Thumbnail"> 
                    <div class="card-body"> 
                        <h8 class="card-title">[[ nb.name ]]</h8> 
                        <p class="card-text">[[ nb.description ]]</p> 
                    </div> 
                </div>`
});


Vue.component('notebook-carousel', {
    delimiters: ['[[', ']]'],
    props: {
        'header': {
            type: String,
            required: false,
            default: ''
        },
        'nblist': {
            type: Array,
            required: true
        },
        'size': {
            type: Number,
            required: false,
            default: 5
        }
    },
    data: function() {
        return {
            'loading': true,
            'page_number': 0
        }
    },
    watch: {
      'nblist': function (new_val, old_val) {
          this.loading = false;
      },
      'loading': function (new_val, old_val) {
          // Hide the loading spinner
          if (!new_val) this.$el.querySelector('.spinner-border').style.display = 'none';
          else this.$el.querySelector('.spinner-border').style.display = 'block';

          // Hide the next/previous buttons if a single page
          if (this.page_count() === 1) this.$el.querySelectorAll('.nb-carousel-button').forEach(n => n.style.display = 'none');
      }
    },
    methods: {
        next_page() {
            console.log(this.page_count());
            console.log(this.size);
            if (this.page_number === this.page_count()-1) this.page_number = 0;
            this.page_number++;
        },
        prev_page() {
            if (this.page_number === 0) this.page_number = this.page_count()-1;
            this.page_number--;
        },
        page_count() {
            let l = this.nblist.length,
                s = this.size;
            return Math.ceil(l/s);
        }
    },
    computed: {
        paginated() {
            const start = this.page_number * this.size,
                  end = start + this.size;

             return this.nblist.slice(start, end);
        }
    },
    template: `<div class="nb-carousel">
                   <div class="float-right show-all"><a href="#">[ Explore All ]</a></div>
                   <h1>[[ header ]]</h1>
                   <div class="nb-carousel-slider">
                       <button class="nb-carousel-button" v-on:click="prev_page">
                           <i class="fas fa-arrow-circle-left"></i>
                       </button>
                       <div class="spinner-border" role="status">
                           <span class="sr-only">Loading...</span>
                       </div>
                       <notebook-card v-for="nb in paginated" :nb="nb"></notebook-card>
                       <button class="nb-carousel-button" v-on:click="next_page">
                           <i class="fas fa-arrow-circle-right"></i>
                       </button>
                   </div>
               </div>`
});