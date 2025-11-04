// Track currently loaded content
let currentContent = null;

// Build breadcrumb trail for current page
function buildBreadcrumb(contentKey) {
  const breadcrumbNav = document.getElementById('breadcrumb');
  const breadcrumbList = breadcrumbNav.querySelector('ol');

  // Clear existing breadcrumbs
  breadcrumbList.innerHTML = '';

  // Always start with Home
  const homeCrumb = document.createElement('li');
  homeCrumb.setAttribute('itemprop', 'itemListElement');
  homeCrumb.setAttribute('itemscope', '');
  homeCrumb.setAttribute('itemtype', 'https://schema.org/ListItem');

  // Check if current page is the first navigation item
  const firstNavItem = getFirstNavigationItem();
  const isFirstNavItem = contentKey === firstNavItem;
  if (isFirstNavItem) {
    // For the first navigation item, show as current page (no link)
    const firstNavLink = document.querySelector('#sidebar .nav-level-1 > li:first-child a[data-content]');
    const pageName = firstNavLink ? firstNavLink.textContent.trim() : 'Home';
    homeCrumb.innerHTML = `
            <span itemprop="name">${pageName}</span>
            <meta itemprop="position" content="1">
        `;
  } else {
    // For other pages, link back to the first navigation item
    const firstNavLink = document.querySelector('#sidebar .nav-level-1 > li:first-child a[data-content]');
    const pageName = firstNavLink ? firstNavLink.textContent.trim() : 'Home';
    homeCrumb.innerHTML = `
            <a href="#" data-content="${firstNavItem}" itemprop="item">
                <span itemprop="name">${pageName}</span>
            </a>
            <meta itemprop="position" content="1">
        `;
  }
  breadcrumbList.appendChild(homeCrumb);

  // Find the current link in the navigation
  const currentLink = document.querySelector(`[data-content="${contentKey}"]`);
  if (!currentLink) return;

  // Build path from current item back to root
  const path = [];
  let element = currentLink;
  while (element) {
    if (element.dataset && element.dataset.content) {
      path.unshift({
        key: element.dataset.content,
        text: element.textContent.trim()
      });
    }

    // Move up to parent link
    const parentUl = element.closest('ul');
    if (!parentUl || parentUl.classList.contains('nav-level-1')) break;
    const parentLi = parentUl.parentElement;
    if (!parentLi || !parentLi.classList.contains('has-children')) break;
    element = parentLi.querySelector('.nav-item-wrapper > a');
  }

  // Add breadcrumb items (skip first if it's the first navigation item since we already added it)
  let position = 2;
  const startIndex = path[0]?.key === firstNavItem ? 1 : 0;
  for (let i = startIndex; i < path.length; i++) {
    const item = path[i];
    const li = document.createElement('li');
    li.setAttribute('itemprop', 'itemListElement');
    li.setAttribute('itemscope', '');
    li.setAttribute('itemtype', 'https://schema.org/ListItem');
    if (i === path.length - 1) {
      // Last item (current page) - no link
      li.innerHTML = `
                <span itemprop="name">${item.text}</span>
                <meta itemprop="position" content="${position}">
            `;
    } else {
      // Parent items - with links
      li.innerHTML = `
                <a href="#" data-content="${item.key}" itemprop="item">
                    <span itemprop="name">${item.text}</span>
                </a>
                <meta itemprop="position" content="${position}">
            `;
    }
    breadcrumbList.appendChild(li);
    position++;
  }

  // Add click handlers to breadcrumb links
  breadcrumbList.querySelectorAll('a[data-content]').forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      loadContent(this.dataset.content);
      expandToActiveItem(this.dataset.content);
    });
  });
}

// Enhance build-time TOC with Navigation section for sub-pages
function enhanceTOCWithNavigation(tocElement, contentKey) {
  // Find the toc-header-left element
  const tocHeaderLeft = tocElement.querySelector('.toc-header-left > ul');
  if (!tocHeaderLeft) {
    return; // No proper structure to enhance
  }

  // Check if navigation section already exists
  if (tocHeaderLeft.querySelector('.toc-section[data-section="navigation"]')) {
    return; // Already has navigation section
  }

  // Check for sub-pages in navigation structure
  const currentLink = document.querySelector(`[data-content="${contentKey}"]`);
  if (!currentLink) {
    return; // Current page not found in navigation
  }
  const parentLi = currentLink.closest('li.has-children');
  if (!parentLi) {
    return; // No children, no navigation section needed
  }
  const childList = parentLi.querySelector(':scope > ul.nav-level-2, :scope > ul.nav-level-3, :scope > ul.nav-level-4');
  if (!childList) {
    return; // No child list found
  }

  // Build navigation items
  const navItems = [];
  const processNavItem = (li, level = 1) => {
    const link = li.querySelector(':scope > a, :scope > .nav-item-wrapper > a');
    if (!link) return null;
    const childKey = link.dataset.content;
    const childText = link.textContent.trim();

    // Skip the current page itself
    if (childKey === contentKey) {
      return null;
    }
    const item = {
      text: childText,
      href: `#${childKey}`,
      dataContent: childKey,
      level: level,
      children: []
    };

    // Check for children
    const hasChildren = li.classList.contains('has-children');
    if (hasChildren) {
      const childUl = li.querySelector(':scope > ul');
      if (childUl) {
        const childLis = childUl.querySelectorAll(':scope > li');
        childLis.forEach(childLi => {
          const childItem = processNavItem(childLi, level + 1);
          if (childItem) {
            item.children.push(childItem);
          }
        });
      }
    }
    return item;
  };
  const topLevelItems = childList.querySelectorAll(':scope > li');
  topLevelItems.forEach(li => {
    const item = processNavItem(li);
    if (item) {
      navItems.push(item);
    }
  });
  if (navItems.length === 0) {
    return; // No sub-pages to show
  }

  // Determine initial state: collapsed if there are page headings
  const hasHeadings = tocElement.querySelector('.toc-section[data-section="headings"]');
  const isCollapsed = hasHeadings;

  // Build navigation section HTML
  const buildNavHTML = items => {
    let html = '';
    items.forEach(item => {
      const className = item.level > 1 ? `toc-item-level-${item.level}` : '';
      html += `<li class="${className}"><a href="${item.href}" data-content="${item.dataContent}">${item.text}</a>`;
      if (item.children.length > 0) {
        html += '<ul>' + buildNavHTML(item.children) + '</ul>';
      }
      html += '</li>';
    });
    return html;
  };

  // Create navigation section
  const navSection = document.createElement('li');
  navSection.className = 'toc-section';
  navSection.innerHTML = `
    <div class="toc-section-header">
      <button class="toc-section-toggle" data-section="navigation">${isCollapsed ? '▶' : '▼'}</button>
      <span class="toc-section-title">Navigation</span>
    </div>
    <ul class="toc-section-content" data-section="navigation"${isCollapsed ? ' style="display: none;"' : ''}>
      ${buildNavHTML(navItems)}
    </ul>
  `;

  // Add navigation section after contents section
  tocHeaderLeft.appendChild(navSection);

  // Add event listener for the new toggle button
  const toggleBtn = navSection.querySelector('.toc-section-toggle');
  toggleBtn.addEventListener('click', () => {
    const section = navSection.querySelector('.toc-section-content');
    const isHidden = section.style.display === 'none';
    section.style.display = isHidden ? '' : 'none';
    toggleBtn.textContent = isHidden ? '▼' : '▶';
  });
}

// Generate table of contents including sub-pages and page headings
function generateTableOfContents(contentKey, htmlContent) {
  // Build a hierarchical structure of TOC items
  let tocItems = [];

  // 1. Check for sub-pages in navigation and build hierarchy
  const currentLink = document.querySelector(`[data-content="${contentKey}"]`);
  if (currentLink) {
    const parentLi = currentLink.closest('li.has-children');
    if (parentLi) {
      const childList = parentLi.querySelector(':scope > ul.nav-level-2, :scope > ul.nav-level-3, :scope > ul.nav-level-4');
      if (childList) {
        const processNavItem = li => {
          const link = li.querySelector(':scope > a, :scope > .nav-item-wrapper > a');
          if (!link) return null;
          const childKey = link.dataset.content;
          const childText = link.textContent.trim();
          const hasChildren = li.classList.contains('has-children');

          // Skip the current page itself - don't include it in its own TOC
          if (childKey === contentKey) {
            // But if it has children, process them
            if (hasChildren) {
              const childUl = li.querySelector(':scope > ul');
              if (childUl) {
                const childLis = childUl.querySelectorAll(':scope > li');
                const childItems = [];
                childLis.forEach(childLi => {
                  const childItem = processNavItem(childLi);
                  if (childItem) {
                    childItems.push(childItem);
                  }
                });
                return childItems; // Return array of children directly
              }
            }
            return null; // Skip this item
          }
          const item = {
            type: 'subpage',
            text: childText,
            href: `#${childKey}`,
            dataContent: childKey,
            children: []
          };

          // Check for children
          if (hasChildren) {
            const childUl = li.querySelector(':scope > ul');
            if (childUl) {
              const childLis = childUl.querySelectorAll(':scope > li');
              childLis.forEach(childLi => {
                const childItem = processNavItem(childLi);
                if (childItem) {
                  // If childItem is an array, spread it
                  if (Array.isArray(childItem)) {
                    item.children.push(...childItem);
                  } else {
                    item.children.push(childItem);
                  }
                }
              });
            }
          }
          return item;
        };
        const topLevelItems = childList.querySelectorAll(':scope > li');
        topLevelItems.forEach(li => {
          const item = processNavItem(li);
          if (item) {
            // If item is an array (from skipping current page), spread it
            if (Array.isArray(item)) {
              tocItems.push(...item);
            } else {
              tocItems.push(item);
            }
          }
        });
      }
    }
  }

  // 2. Extract h2, h3 and h4 headings from content and organize hierarchically
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = htmlContent;
  const headings = tempDiv.querySelectorAll('h2, h3, h4');
  const headingItems = [];
  let currentH2 = null;
  let currentH3 = null;

  // Helper function to generate URL-friendly IDs from heading text
  const generateHeadingId = (text, index) => {
    // Convert to lowercase, replace spaces with hyphens, remove special characters
    let id = text.toLowerCase().replace(/[^\w\s-]/g, '') // Remove special characters except spaces and hyphens
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/--+/g, '-') // Replace multiple hyphens with single hyphen
    .replace(/^-+|-+$/g, ''); // Trim hyphens from start/end

    // If the ID is empty or too short, use a numbered fallback
    if (!id || id.length < 2) {
      id = `heading-${index}`;
    }
    return id;
  };
  headings.forEach((heading, index) => {
    const headingText = heading.textContent.trim();

    // Skip headings that end with a colon (they are category headers, not linkable sections)
    if (headingText.endsWith(':')) {
      return;
    }
    const headingId = generateHeadingId(headingText, index);
    const level = heading.tagName.toLowerCase();
    const item = {
      type: 'heading',
      level: level,
      text: headingText,
      href: `#${contentKey}:${headingId}`,
      id: headingId,
      children: []
    };
    if (level === 'h2') {
      headingItems.push(item);
      currentH2 = item; // Update current H2
      currentH3 = null; // Reset H3 when we encounter a new H2
    } else if (level === 'h3') {
      if (currentH2) {
        // Add H3 as child of the most recent H2
        currentH2.children.push(item);
      } else {
        // If no H2 exists yet, add H3 as top-level item
        headingItems.push(item);
      }
      currentH3 = item; // Always update currentH3 when we encounter a new H3
    } else if (level === 'h4') {
      if (currentH3) {
        // Add H4 as child of the most recent H3
        currentH3.children.push(item);
      } else if (currentH2) {
        // If no H3 but H2 exists, add H4 as child of H2
        currentH2.children.push(item);
      } else {
        // If neither H2 nor H3 exists, add H4 as top-level item
        headingItems.push(item);
      }
    }
  });

  // Reorder: headings first, then sub-pages
  const allTocItems = [...headingItems, ...tocItems];

  // If no items, return null
  if (allTocItems.length === 0) return null;

  // Build the TOC HTML with collapsible header and tree structure
  const buildTocItem = (item, isTopLevel = false) => {
    const hasChildren = item.children && item.children.length > 0;
    const isHeading = item.type === 'heading';
    let html = '<li class="';
    if (item.type === 'subpage') {
      html += 'toc-subpage';
    } else if (item.level === 'h2') {
      html += 'toc-h2';
    } else if (item.level === 'h3') {
      html += 'toc-h3';
    } else if (item.level === 'h4') {
      html += 'toc-h4';
    }
    // Only make headings collapsible, not sub-pages
    if (hasChildren && isHeading) {
      html += ' toc-item';
      // Start expanded by default
    }
    html += '">';
    if (item.type === 'subpage') {
      html += `<a href="${item.href}" data-content="${item.dataContent}">${item.text}</a>`;
    } else {
      // For headings, wrap in a clickable div if they have children
      if (hasChildren && isHeading) {
        html += '<div class="toc-item-wrapper">';
      }
      html += `<a href="${item.href}">${item.text}</a>`;
      if (hasChildren && isHeading) {
        html += '</div>';
      }
    }
    if (hasChildren && isHeading) {
      html += '<ul class="toc-children">';
      item.children.forEach(child => {
        html += buildTocItem(child, false);
      });
      html += '</ul>';
    } else if (hasChildren && item.type === 'subpage') {
      // For sub-pages, just render children directly without collapse functionality
      html += '<ul class="toc-children" style="max-height: none;">';
      item.children.forEach(child => {
        html += buildTocItem(child, false);
      });
      html += '</ul>';
    }
    html += '</li>';
    return html;
  };
  let tocHtml = '<div class="table-of-contents">';
  tocHtml += '<div class="toc-header">';
  tocHtml += '<div class="toc-header-left">';
  tocHtml += '<ul>';

  // Add headings section with its own collapse button
  let hasHeadings = headingItems.length > 0;
  let hasNavigation = tocItems.length > 0;
  if (hasHeadings) {
    // CONTENTS section starts expanded if there are headings
    tocHtml += '<li class="toc-section">';
    tocHtml += '<div class="toc-section-header">';
    tocHtml += '<button class="toc-section-toggle" data-section="headings">▼</button>';
    tocHtml += '<span class="toc-section-title">Contents</span>';
    tocHtml += '</div>';
    tocHtml += '<ul class="toc-section-content" data-section="headings">';
    headingItems.forEach(item => {
      tocHtml += buildTocItem(item, true);
    });
    tocHtml += '</ul>';
    tocHtml += '</li>';
  }

  // Add divider if we have both headings and sub-pages
  if (hasHeadings && hasNavigation) {
    tocHtml += '<li class="toc-divider"></li>';
  }

  // Add sub-pages section with its own collapse button
  // Starts collapsed if there are headings, expanded if there are no headings but there is navigation
  if (hasNavigation) {
    let navigationClass = hasHeadings ? 'collapsed' : '';
    tocHtml += `<li class="toc-section ${navigationClass}">`;
    tocHtml += '<div class="toc-section-header">';
    tocHtml += '<button class="toc-section-toggle" data-section="navigation">▼</button>';
    tocHtml += '<span class="toc-section-title">Navigation</span>';
    tocHtml += '</div>';
    tocHtml += '<ul class="toc-section-content" data-section="navigation">';
    tocItems.forEach(item => {
      tocHtml += buildTocItem(item, true);
    });
    tocHtml += '</ul>';
    tocHtml += '</li>';
  }
  tocHtml += '</ul>'; // Close left column ul
  tocHtml += '</div>'; // Close toc-header-left
  tocHtml += '<div class="toc-header-right">';
  tocHtml += '<button class="toc-toggle" aria-label="Toggle table of contents">▼</button>';
  tocHtml += '</div>'; // Close toc-header-right
  tocHtml += '</div>'; // Close toc-header
  tocHtml += '</div>'; // Close table-of-contents

  return {
    html: tocHtml,
    headingIds: headingItems.flatMap(item => {
      const ids = item.id ? [item] : [];
      if (item.children) {
        ids.push(...item.children.filter(c => c.id));
      }
      return ids;
    })
  };
}

// Update page metadata (title and description) for SEO
function updatePageMetadata(contentKey, contentDiv) {
  // Get the main heading (h2) from the content
  const mainHeading = contentDiv.querySelector('h2');
  const pageTitle = mainHeading ? mainHeading.textContent.trim() : formatPageTitle(contentKey);

  // Get the first paragraph for description
  const firstParagraph = contentDiv.querySelector('p');
  const description = firstParagraph ? firstParagraph.textContent.trim().substring(0, 160) + '...' : 'Welcome to GAZ Tank. Explore our content and resources.';

  // Update document title
  document.title = `${pageTitle} - GAZ Tank`;

  // Update meta description
  let metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute('content', description);
  }

  // Update Open Graph title
  let ogTitle = document.querySelector('meta[property="og:title"]');
  if (ogTitle) {
    ogTitle.setAttribute('content', `${pageTitle} - GAZ Tank`);
  }

  // Update Open Graph description
  let ogDescription = document.querySelector('meta[property="og:description"]');
  if (ogDescription) {
    ogDescription.setAttribute('content', description);
  }

  // Update Open Graph URL
  let ogUrl = document.querySelector('meta[property="og:url"]');
  if (ogUrl) {
    ogUrl.setAttribute('content', `https://mygaztank.com/#${contentKey}`);
  }

  // Update Twitter title
  let twitterTitle = document.querySelector('meta[name="twitter:title"]');
  if (twitterTitle) {
    twitterTitle.setAttribute('content', `${pageTitle} - GAZ Tank`);
  }

  // Update Twitter description
  let twitterDescription = document.querySelector('meta[name="twitter:description"]');
  if (twitterDescription) {
    twitterDescription.setAttribute('content', description);
  }

  // Update Twitter URL
  let twitterUrl = document.querySelector('meta[name="twitter:url"]');
  if (twitterUrl) {
    twitterUrl.setAttribute('content', `https://mygaztank.com/#${contentKey}`);
  }

  // Update canonical URL
  let canonical = document.querySelector('link[rel="canonical"]');
  if (canonical) {
    canonical.setAttribute('href', `https://mygaztank.com/#${contentKey}`);
  }
}

// Format content key into a readable title
function formatPageTitle(contentKey) {
  return contentKey.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Display hashtags from data-hashtags attribute
function displayHashtags(contentElement) {
  const hashtagArea = document.getElementById('hashtag-area');

  // Clear existing hashtags
  hashtagArea.innerHTML = '';

  // Look for data-hashtags attribute in the content
  const taggedElement = contentElement.querySelector('[data-hashtags]');
  if (taggedElement) {
    const tagsAttr = taggedElement.getAttribute('data-hashtags');
    if (tagsAttr && tagsAttr.trim()) {
      // Split by comma, trim whitespace, and create hashtag elements
      const tags = tagsAttr.split(',').map(tag => tag.trim()).filter(tag => tag);
      tags.forEach(tag => {
        const hashtagSpan = document.createElement('span');
        hashtagSpan.className = 'hashtag';
        hashtagSpan.textContent = '#' + tag;
        hashtagArea.appendChild(hashtagSpan);
      });
    }
  }
}

// Enable lazy loading for all images in content
function enableLazyLoading() {
  const pageContent = document.getElementById('page-content');

  // Find all images in the loaded content
  const images = pageContent.querySelectorAll('img');
  images.forEach(img => {
    // Skip images that should not be lazy loaded:
    // 1. Images with data-no-lazy attribute
    // 2. Images with 'no-lazy' class
    // 3. Images already marked with loading="eager"
    // 4. Images that already have loading attribute set
    if (img.hasAttribute('data-no-lazy') || img.classList.contains('no-lazy') || img.getAttribute('loading') === 'eager') {
      return; // Skip this image
    }

    // Only add lazy loading if not already set
    if (!img.hasAttribute('loading')) {
      img.setAttribute('loading', 'lazy');
    }

    // Ensure images are responsive
    if (!img.style.maxWidth) {
      img.style.maxWidth = '100%';
      img.style.height = 'auto';
    }
  });
}

// Load content from external files
async function loadContent(contentKey, saveToStorage = true, updateHash = true) {
  const pageContent = document.getElementById('page-content');

  // Check if the requested content is already loaded
  if (currentContent === contentKey) {
    return;
  }
  try {
    // Fetch content from the corresponding HTML file
    const response = await fetch(`content/${contentKey}.html`);
    if (!response.ok) {
      throw new Error(`Failed to load content: ${response.status}`);
    }
    const html = await response.text();

    // Create a temporary container to parse the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // Check if TOC already exists in the HTML (from build-time generation)
    const existingToc = tempDiv.querySelector('nav.table-of-contents');
    let tocResult = null;
    if (!existingToc) {
      // No build-time TOC found - generate one dynamically
      // This fallback handles pages without h2/h3/h4 headings
      tocResult = generateTableOfContents(contentKey, html);

      // Add IDs to h3 and h4 headings for anchor links
      if (tocResult && tocResult.headingIds) {
        const headings = tempDiv.querySelectorAll('h3, h4');
        tocResult.headingIds.forEach((item, index) => {
          if (headings[index]) {
            headings[index].id = item.id;
          }
        });
      }

      // Insert TOC after the first heading if available
      if (tocResult) {
        // Check for h1 first (page title), then fall back to h2
        const firstHeading = tempDiv.querySelector('h1') || tempDiv.querySelector('h2');
        if (firstHeading) {
          // Insert TOC after the first heading (h1 or h2)
          const tocDiv = document.createElement('div');
          tocDiv.innerHTML = tocResult.html;
          firstHeading.insertAdjacentElement('afterend', tocDiv.firstElementChild);
        } else {
          // No heading found, put TOC at the beginning
          tempDiv.innerHTML = tocResult.html + tempDiv.innerHTML;
        }
      }
    } else {
      // Build-time TOC exists - enhance it with navigation section if needed
      enhanceTOCWithNavigation(existingToc, contentKey);
    }

    // Set page content (with either build-time or runtime TOC)
    pageContent.innerHTML = tempDiv.innerHTML;

    // Display hashtags if present in data-tags attribute
    displayHashtags(tempDiv);

    // Enable lazy loading for all images in the content
    enableLazyLoading();

    // Apply syntax highlighting to code blocks
    if (typeof Prism !== 'undefined') {
      Prism.highlightAllUnder(pageContent);
    }

    // Render Mermaid diagrams if present
    if (typeof mermaid !== 'undefined') {
      // Find all mermaid blocks and render them
      const mermaidBlocks = pageContent.querySelectorAll('pre.mermaid');
      if (mermaidBlocks.length > 0) {
        mermaid.run({
          nodes: mermaidBlocks,
          suppressErrors: true
        });
      }
    }

    // Add click handlers to TOC links and toggle button
    // Works with both build-time generated TOCs and runtime generated TOCs
    const tocContainer = pageContent.querySelector('.table-of-contents, nav.table-of-contents');
    if (tocContainer) {
      // TOC toggle button (collapse entire TOC)
      const tocToggle = tocContainer.querySelector('.toc-toggle');
      const tocHeader = tocContainer.querySelector('.toc-header');
      if (tocToggle && tocHeader) {
        // Load saved state from sessionStorage
        const tocState = sessionStorage.getItem(`toc-collapsed-${contentKey}`);
        if (tocState === 'true') {
          tocContainer.classList.add('collapsed');
        }

        // Toggle on button click
        tocToggle.addEventListener('click', function (e) {
          e.stopPropagation();
          tocContainer.classList.toggle('collapsed');
          // Save state
          sessionStorage.setItem(`toc-collapsed-${contentKey}`, tocContainer.classList.contains('collapsed'));
        });

        // Click on header (ellipsis area) when collapsed to expand
        tocHeader.addEventListener('click', function (e) {
          // Only expand if TOC is collapsed and not clicking on interactive elements
          if (tocContainer.classList.contains('collapsed') && !e.target.closest('.toc-toggle') && !e.target.closest('.toc-section-toggle')) {
            tocContainer.classList.remove('collapsed');
            // Save state
            sessionStorage.setItem(`toc-collapsed-${contentKey}`, false);
          }
        });
      }

      // TOC section toggle buttons (collapse headings or sub-pages sections)
      pageContent.querySelectorAll('.toc-section-toggle').forEach(toggle => {
        toggle.addEventListener('click', function (e) {
          e.stopPropagation();
          const section = this.closest('.toc-section');
          if (section) {
            section.classList.toggle('collapsed');
            // Save state using section data attribute
            const sectionName = section.dataset.section;
            sessionStorage.setItem(`toc-section-${contentKey}-${sectionName}`, section.classList.contains('collapsed'));
          }
        });
      });

      // Restore TOC section states from sessionStorage (if saved state exists)
      pageContent.querySelectorAll('.toc-section').forEach(section => {
        const sectionName = section.dataset.section;
        const sectionState = sessionStorage.getItem(`toc-section-${contentKey}-${sectionName}`);
        // Only apply saved state if it exists, otherwise keep the default state from HTML
        if (sectionState !== null) {
          if (sectionState === 'true') {
            section.classList.add('collapsed');
          } else {
            section.classList.remove('collapsed');
          }
        }
      });

      // TOC item wrappers (collapse individual heading tree items only)
      pageContent.querySelectorAll('.toc-item-wrapper').forEach(wrapper => {
        wrapper.addEventListener('click', function (e) {
          // Only toggle if clicking the wrapper itself or the ::before pseudo-element area
          // Don't toggle if clicking the link
          if (e.target.tagName === 'A') {
            return; // Let the link click handler handle it
          }
          e.preventDefault();
          e.stopPropagation();
          const parentLi = this.closest('.toc-item');
          if (parentLi) {
            parentLi.classList.toggle('collapsed');

            // Save state using heading text (since headings don't have data-content)
            const itemLink = parentLi.querySelector('a');
            if (itemLink) {
              const headingText = itemLink.textContent.trim();
              sessionStorage.setItem(`toc-heading-${contentKey}-${headingText}`, parentLi.classList.contains('collapsed'));
            }
          }
        });
      });

      // Also handle clicks on the parent .toc-item itself (for the ::before arrow area)
      pageContent.querySelectorAll('.toc-item').forEach(item => {
        item.addEventListener('click', function (e) {
          // Only handle clicks on the li itself or the ::before pseudo-element area (left padding)
          // Don't handle if clicking on child elements
          const rect = this.getBoundingClientRect();
          const clickX = e.clientX - rect.left;

          // If click is in the left 1.5rem (where the arrow is), toggle
          if (clickX >= 0 && clickX <= 24) {
            // ~1.5rem in pixels
            e.preventDefault();
            e.stopPropagation();
            this.classList.toggle('collapsed');

            // Save state using heading text
            const itemLink = this.querySelector('a');
            if (itemLink) {
              const headingText = itemLink.textContent.trim();
              sessionStorage.setItem(`toc-heading-${contentKey}-${headingText}`, this.classList.contains('collapsed'));
            }
          }
        });
      });

      // Restore TOC item states from sessionStorage (only for headings)
      pageContent.querySelectorAll('.toc-item').forEach(item => {
        // Check if this is a heading item (not a subpage)
        const itemLink = item.querySelector('a');
        const isSubpage = itemLink && itemLink.hasAttribute('data-content');
        if (!isSubpage) {
          // This is a heading item - restore its state
          const headingText = itemLink ? itemLink.textContent.trim() : '';
          const itemState = sessionStorage.getItem(`toc-heading-${contentKey}-${headingText}`);
          if (itemState === 'true') {
            item.classList.add('collapsed');
          }
        }
      });

      // Sub-page navigation links
      pageContent.querySelectorAll('.table-of-contents a[data-content]').forEach(link => {
        link.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation(); // Prevent header toggle when clicking links
          const key = this.dataset.content;
          loadContent(key);
          expandToActiveItem(key);
        });
      });

      // Heading anchor links (smooth scroll)
      pageContent.querySelectorAll('.table-of-contents a:not([data-content]), nav.table-of-contents a:not([data-content])').forEach(link => {
        link.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation(); // Prevent header toggle when clicking links
          const href = this.getAttribute('href').substring(1); // Remove #

          // Check if it's a cross-page link (format: pagename:heading-id)
          if (href.includes(':')) {
            const [pageName, headingId] = href.split(':');
            // Update URL hash for navigation
            window.location.hash = href;
          } else {
            // Same-page heading link (build-time generated IDs are just #heading-id)
            const targetElement = document.getElementById(href);
            if (targetElement) {
              targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
              });
              // Update URL hash to include page for bookmarking
              window.location.hash = `${contentKey}:${href}`;
            }
          }
        });
      });
    }

    // Convert internal content links (hash links like #setup/PAGE) to use SPA routing
    pageContent.querySelectorAll('a[href^="#setup/"], a[href^="#content/"]').forEach(link => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        const contentKey = href.substring(1); // Remove the #
        // Add data-content attribute for SPA routing
        link.setAttribute('data-content', contentKey);
        // Add click handler
        link.addEventListener('click', function (e) {
          e.preventDefault();
          loadContent(contentKey);
          expandToActiveItem(contentKey);
        });
      }
    });

    // Handle ALL internal anchor links (e.g., from markdown TOCs embedded in content)
    // This catches any <a href="#heading-id"> links that aren't in the generated TOC
    pageContent.querySelectorAll('a[href^="#"]').forEach(link => {
      const href = link.getAttribute('href');

      // Skip if already handled (has data-content or is in TOC)
      if (link.hasAttribute('data-content') || link.closest('.table-of-contents, nav.table-of-contents')) {
        return;
      }

      // Skip if it's a content page link (#setup/PAGE or #content/PAGE)
      if (href.includes('/')) {
        return;
      }

      // Handle as same-page anchor link
      link.addEventListener('click', function (e) {
        e.preventDefault();
        const anchorId = href.substring(1); // Remove #

        // Check if it's a cross-page link (format: pagename:heading-id)
        if (anchorId.includes(':')) {
          const [pageName, headingId] = anchorId.split(':');
          // Update URL hash for navigation
          window.location.hash = anchorId;
        } else {
          // Same-page heading link
          const targetElement = document.getElementById(anchorId);
          if (targetElement) {
            targetElement.scrollIntoView({
              behavior: 'smooth',
              block: 'start'
            });
            // Update URL hash to include page for bookmarking
            window.location.hash = `${contentKey}:${anchorId}`;
          }
        }
      });
    });

    // Update current content tracker
    currentContent = contentKey;

    // Update page title and meta description for SEO
    updatePageMetadata(contentKey, tempDiv);

    // Update URL hash for direct linking
    if (updateHash) {
      window.location.hash = contentKey;
    }

    // Build breadcrumb navigation
    buildBreadcrumb(contentKey);

    // Save the current page to sessionStorage so it persists on refresh
    if (saveToStorage) {
      sessionStorage.setItem('currentPage', contentKey);
    }

    // Update active state in navigation
    document.querySelectorAll('#sidebar a').forEach(link => {
      link.classList.remove('active');
      link.classList.remove('active-parent');
    });

    // Add active class to current page link
    const activeLink = document.querySelector(`[data-content="${contentKey}"]`);
    if (activeLink && activeLink.closest('#sidebar')) {
      activeLink.classList.add('active');

      // Add active-parent class to the top-level parent (not active)
      const topLevelParent = activeLink.closest('.nav-level-1 > li');
      if (topLevelParent) {
        const topLevelLink = topLevelParent.querySelector(':scope > a, :scope > .nav-item-wrapper > a');
        if (topLevelLink && topLevelLink !== activeLink) {
          topLevelLink.classList.add('active-parent');
        }
      }
    }

    // Set focus to parent page breadcrumb for keyboard accessibility
    // This gives keyboard users immediate access to navigation context
    setTimeout(() => {
      const breadcrumbNav = document.getElementById('breadcrumb');
      if (breadcrumbNav) {
        const breadcrumbItems = breadcrumbNav.querySelectorAll('li');

        // Focus on second-to-last breadcrumb item (the parent page)
        // Last item is current page (span), second-to-last is parent (link)
        if (breadcrumbItems.length >= 2) {
          // Get the second-to-last item (parent page)
          const parentItem = breadcrumbItems[breadcrumbItems.length - 2];
          const parentLink = parentItem.querySelector('a');
          if (parentLink) {
            parentLink.focus();
          } else {
            // If no link (shouldn't happen), try first link available
            const firstLink = breadcrumbNav.querySelector('a');
            if (firstLink) firstLink.focus();
          }
        } else if (breadcrumbItems.length === 1) {
          // Only Home breadcrumb - shouldn't have a link on home page
          // but if we're here, don't focus anything
        }
      }
    }, 100);
  } catch (error) {
    console.error('Error loading content:', error);
    pageContent.innerHTML = `<h2>Error</h2><p>Failed to load content. Please try again.</p>`;
    currentContent = null; // Reset on error
    if (saveToStorage) {
      sessionStorage.removeItem('currentPage');
    }
  }
}

/**
 * Get the first navigation item's content key
 * @returns {string} The data-content value of the first navigation link
 */
function getFirstNavigationItem() {
  const firstNavLink = document.querySelector('#sidebar .nav-level-1 > li:first-child a[data-content]');
  return firstNavLink ? firstNavLink.dataset.content : 'home'; // fallback to 'home' if not found
}

// Get content key from URL hash
function getContentFromHash() {
  const hash = window.location.hash.slice(1); // Remove # symbol
  if (!hash) return null;

  // Check if hash contains a heading anchor (format: pagename:heading-id)
  if (hash.includes(':')) {
    const [pageName, headingId] = hash.split(':');
    return {
      page: pageName,
      heading: headingId
    };
  }
  return {
    page: hash,
    heading: null
  };
}

// Scroll to a heading after content loads
function scrollToHeading(headingId) {
  // Wait a bit for the content to render
  setTimeout(() => {
    const headingElement = document.getElementById(headingId);
    if (headingElement) {
      headingElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }, 100);
}

// Toggle navigation submenu
function toggleSubmenu(button) {
  const parentLi = button.closest('.has-children');
  if (parentLi) {
    parentLi.classList.toggle('expanded');

    // Save expanded state to sessionStorage
    saveExpandedState();
  }
}

// Save which menu items are expanded
function saveExpandedState() {
  const expandedItems = [];
  document.querySelectorAll('.has-children.expanded > .nav-item-wrapper > a').forEach(link => {
    if (link.dataset.content) {
      expandedItems.push(link.dataset.content);
    }
  });
  sessionStorage.setItem('expandedMenuItems', JSON.stringify(expandedItems));
}

// Restore expanded state from sessionStorage
function restoreExpandedState() {
  const savedExpanded = sessionStorage.getItem('expandedMenuItems');
  if (savedExpanded) {
    try {
      const expandedItems = JSON.parse(savedExpanded);
      expandedItems.forEach(contentKey => {
        const link = document.querySelector(`[data-content="${contentKey}"]`);
        if (link) {
          const parentLi = link.closest('.has-children');
          if (parentLi) {
            parentLi.classList.add('expanded');
          }
        }
      });
    } catch (e) {
      console.error('Error restoring expanded state:', e);
    }
  }
}

// Expand parent menus to show the active item
function expandToActiveItem(contentKey) {
  const activeLink = document.querySelector(`[data-content="${contentKey}"]`);
  if (activeLink) {
    let parentLi = activeLink.closest('li').parentElement.closest('.has-children');
    while (parentLi) {
      parentLi.classList.add('expanded');
      parentLi = parentLi.parentElement.closest('.has-children');
    }
    saveExpandedState();
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function () {
  // Update copyright year
  const currentYear = new Date().getFullYear();
  const copyrightYearElement = document.getElementById('copyright-year');
  if (copyrightYearElement) {
    // Only show "-currentYear" if it's different from 2025
    copyrightYearElement.textContent = currentYear > 2025 ? `-${currentYear}` : '';
  }

  // Add toggle handlers for expandable menu items
  document.querySelectorAll('.nav-toggle').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleSubmenu(this);
    });
  });

  // Add click handlers to all navigation links
  document.querySelectorAll('[data-content]').forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const contentKey = this.dataset.content;

      // Check if this link has children (is a parent menu item)
      const parentLi = this.closest('li.has-children');
      if (parentLi) {
        // If it has children and is not expanded, expand it
        if (!parentLi.classList.contains('expanded')) {
          parentLi.classList.add('expanded');
          saveExpandedState();
        }
        // If already expanded, do nothing (just proceed to load content)
      }
      loadContent(contentKey);
      expandToActiveItem(contentKey);
    });
  });

  // Determine which page to load (priority: URL hash > sessionStorage > first nav item)
  const hashResult = getContentFromHash();
  const savedPage = sessionStorage.getItem('currentPage');
  const firstNavItem = getFirstNavigationItem();
  const pageToLoad = hashResult?.page || savedPage || firstNavItem;
  const headingToScroll = hashResult?.heading;

  // Restore expanded menu state
  restoreExpandedState();

  // Load the determined page - await to ensure it loads first
  // Don't update hash if we're loading from hash (prevents duplicate in history)
  await loadContent(pageToLoad, true, !hashResult);

  // Expand parent menus to show the active item
  expandToActiveItem(pageToLoad);

  // Scroll to heading if specified
  if (headingToScroll) {
    scrollToHeading(headingToScroll);
  }

  // Setup sidebar toggle functionality
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  const mainContainer = document.querySelector('.main-container');
  if (sidebarToggle && sidebar && mainContainer) {
    // Restore sidebar state from sessionStorage
    const sidebarCollapsed = sessionStorage.getItem('sidebar-collapsed');
    // Default to collapsed on mobile (768px or less), otherwise respect saved state
    if (sidebarCollapsed === 'true' || window.innerWidth <= 768) {
      sidebar.classList.add('collapsed');
      mainContainer.classList.add('sidebar-collapsed');
    }

    // Toggle sidebar on button click
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('collapsed');
      mainContainer.classList.toggle('sidebar-collapsed');

      // Save state
      const isCollapsed = sidebar.classList.contains('collapsed');
      sessionStorage.setItem('sidebar-collapsed', isCollapsed);
    });
  }
});

// Handle hash changes (browser back/forward buttons)
window.addEventListener('hashchange', function () {
  const hashResult = getContentFromHash();
  if (hashResult) {
    // Load content without updating hash (already changed)
    loadContent(hashResult.page, true, false);
    expandToActiveItem(hashResult.page);

    // Scroll to heading if specified
    if (hashResult.heading) {
      scrollToHeading(hashResult.heading);
    }
  } else {
    // No hash, load the first navigation item
    const firstNavItem = getFirstNavigationItem();
    loadContent(firstNavItem);
    expandToActiveItem(firstNavItem);
  }
});