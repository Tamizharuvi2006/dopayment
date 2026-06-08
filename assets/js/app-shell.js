(function () {
  const isModulePage = location.pathname.includes('/modules/');
  const loginPath = isModulePage ? '../index.html' : 'index.html';

  function ensureMobileNavigation() {
    const sidebar = document.querySelector('.sidebar');
    const topbar = document.querySelector('.topbar');
    if (!sidebar || !topbar || document.querySelector('.mobile-menu-toggle')) return;

    const toggle = document.createElement('button');
    toggle.className = 'mobile-menu-toggle';
    toggle.type = 'button';
    toggle.setAttribute('aria-label', 'Open navigation');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.innerHTML = '<span aria-hidden="true"></span>';

    const backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';

    function setOpen(open) {
      document.body.classList.toggle('sidebar-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    }

    toggle.addEventListener('click', () => setOpen(!document.body.classList.contains('sidebar-open')));
    backdrop.addEventListener('click', () => setOpen(false));
    sidebar.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setOpen(false)));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
        document.querySelectorAll('.modal-overlay.open').forEach((modal) => modal.classList.remove('open'));
      }
    });

    topbar.prepend(toggle);
    document.body.appendChild(backdrop);
  }

  function normalizeUserChip() {
    const user = JSON.parse(localStorage.getItem('dp_user') || 'null');
    if (!user) return;
    document.querySelectorAll('.user-role, #uRole, #userRole').forEach((roleEl) => {
      const role = user.role || 'user';
      const labels = {
        retailer_supermarket: 'Supermarket Retailer',
        distributor: 'Distributor Hub',
        super_stockist: 'Super Stockist HQ'
      };
      roleEl.textContent = labels[role] || role.charAt(0).toUpperCase() + role.slice(1).replace(/_/g, ' ');
    });
  }

  function wireSignOutButtons() {
    document.querySelectorAll('button[onclick*="dp_user"]').forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        localStorage.removeItem('dp_user');
        window.location.href = loginPath;
      });
    });
  }

  window.initializeSharedState = function () {
    if (localStorage.getItem('dp_wallets')) return;

    const wallets = {
      retailer_supermarket: 0.00,
      merchant_bank_account: 50000.00,
      distributor_pepsi: 120000.00,
      distributor_britannia: 85000.00,
      stockist_pepsi: 450000.00,
      stockist_britannia: 320000.00,
      // Direct-channel wallets (no distributor middleman)
      direct_stockist_pepsi: 28000.00,
      direct_stockist_britannia: 14500.00
    };
    localStorage.setItem('dp_wallets', JSON.stringify(wallets));

    const distributors = [
      { id: 'pepsi',     name: 'PepsiCo Distributor A',           upi: 'distributor.pepsi@okhdfc',     stockist: 'stockist_pepsi',     margin: 12.5 },
      { id: 'britannia', name: 'Britannia & Cadbury Distributor B', upi: 'distributor.britannia@okaxis', stockist: 'stockist_britannia', margin: 12.5 }
    ];
    localStorage.setItem('dp_distributors', JSON.stringify(distributors));

    const stockists = [
      { id: 'stockist_pepsi',     name: 'PepsiCo Super Stockist X',   upi: 'stockist.pepsi@okicici',     margin: 12.5 },
      { id: 'stockist_britannia', name: 'Britannia Super Stockist Y',  upi: 'stockist.britannia@oksbi',   margin: 12.5 }
    ];
    localStorage.setItem('dp_stockists', JSON.stringify(stockists));

    const products = [
      // 3-way chain products (via distributor)
      { id: 'p1', name: 'Pepsi Bottle (1.5L)',     barcode: '890120240011', price:  90.00, cost: 72.00, distributorId: 'pepsi',     stock: 150, channel: 'chain'  },
      { id: 'p2', name: 'Surf Excel Wash (1kg)',    barcode: '890120240022', price: 140.00, cost:112.00, distributorId: 'pepsi',     stock:  80, channel: 'chain'  },
      { id: 'p3', name: 'Good Day Biscuit Pack',    barcode: '890120240033', price:  40.00, cost: 32.00, distributorId: 'britannia', stock: 300, channel: 'chain'  },
      { id: 'p4', name: 'Dairy Milk Chocolate',     barcode: '890120240044', price:  50.00, cost: 40.00, distributorId: 'britannia', stock: 240, channel: 'chain'  },
      // 2-way direct products (Supermarket → Super Stockist directly, no distributor)
      { id: 'p5', name: 'Lay\'s Classic Chips (26g)', barcode: '890120240055', price:  20.00, cost: 14.00, stockistId: 'stockist_pepsi',     stock: 500, channel: 'direct', retailerMarginPct: 30 },
      { id: 'p6', name: 'Kurkure Masala Munch',       barcode: '890120240066', price:  20.00, cost: 14.00, stockistId: 'stockist_pepsi',     stock: 400, channel: 'direct', retailerMarginPct: 30 },
      { id: 'p7', name: 'Britannia Marie Gold (250g)', barcode: '890120240077', price:  30.00, cost: 21.00, stockistId: 'stockist_britannia', stock: 350, channel: 'direct', retailerMarginPct: 30 }
    ];
    localStorage.setItem('dp_products', JSON.stringify(products));

    const templates = [];
    localStorage.setItem('dp_templates', JSON.stringify(templates));

    const now = Date.now();
    const ledger = [
      {
        id: 'TXN-90284', type: 'supermarket_checkout',
        productName: 'Pepsi Bottle (1.5L) x 2',
        totalAmount: 180.00,
        date: new Date(now - 4 * 3600000).toISOString(),
        details: { retailerMargin: 36.00, distributorShare: 144.00, distributorName: 'PepsiCo Distributor A', distributorUpi: 'distributor.pepsi@okhdfc', distributorId: 'pepsi', distributorMargin: 18.00, stockistShare: 126.00, stockistId: 'stockist_pepsi', stockistName: 'PepsiCo Super Stockist X', stockistUpi: 'stockist.pepsi@okicici' },
        status: 'settled', channel: 'chain'
      },
      {
        id: 'TXN-90282', type: 'supermarket_checkout',
        productName: 'Good Day Biscuit Pack x 5, Dairy Milk x 2',
        totalAmount: 300.00,
        date: new Date(now - 24 * 3600000).toISOString(),
        details: { retailerMargin: 60.00, distributorShare: 240.00, distributorName: 'Britannia & Cadbury Distributor B', distributorUpi: 'distributor.britannia@okaxis', distributorId: 'britannia', distributorMargin: 30.00, stockistShare: 210.00, stockistId: 'stockist_britannia', stockistName: 'Britannia Super Stockist Y', stockistUpi: 'stockist.britannia@oksbi' },
        status: 'settled', channel: 'chain'
      },
      // Seeded direct-channel transactions
      {
        id: 'TXN-90279', type: 'direct_checkout',
        productName: "Lay's Classic Chips x 4",
        totalAmount: 80.00,
        date: new Date(now - 6 * 3600000).toISOString(),
        details: { retailerMargin: 24.00, stockistShare: 56.00, stockistId: 'stockist_pepsi', stockistName: 'PepsiCo Super Stockist X', stockistUpi: 'stockist.pepsi@okicici' },
        status: 'settled', channel: 'direct'
      },
      {
        id: 'TXN-90276', type: 'direct_checkout',
        productName: 'Britannia Marie Gold x 6',
        totalAmount: 180.00,
        date: new Date(now - 32 * 3600000).toISOString(),
        details: { retailerMargin: 54.00, stockistShare: 126.00, stockistId: 'stockist_britannia', stockistName: 'Britannia Super Stockist Y', stockistUpi: 'stockist.britannia@oksbi' },
        status: 'settled', channel: 'direct'
      }
    ];
    localStorage.setItem('dp_ledger', JSON.stringify(ledger));
  };

  function installChartDefaults() {
    if (!window.Chart) return;
    Chart.defaults.color = '#475569';
    Chart.defaults.borderColor = '#E2E8F0';
    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.plugins.tooltip.backgroundColor = '#FFFFFF';
    Chart.defaults.plugins.tooltip.titleColor = '#0F172A';
    Chart.defaults.plugins.tooltip.bodyColor = '#475569';
    Chart.defaults.plugins.tooltip.borderColor = '#E2E8F0';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.boxShadow = '0 4px 16px rgba(15,23,42,0.12)';
  }

  installChartDefaults();

  document.addEventListener('DOMContentLoaded', () => {
    ensureMobileNavigation();
    if (!localStorage.getItem('dp_wallets')) {
      window.initializeSharedState();
    }
    normalizeUserChip();
    wireSignOutButtons();
    installChartDefaults();
  });
}());
