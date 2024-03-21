odoo.define('steam_custom.CustomProductItem', function(require) {
    'use strict';

    const ProductItem = require('point_of_sale.ProductItem');

    class CustomProductItem extends ProductItem {
        async getStock() {
            const productId = this.props.product.id;
            const stock = await this.rpc({
                model: 'stock.quant',
                method: 'search_read',
                domain: [['product_id', '=', productId]],
                fields: ['product_id', 'quantity'],
                limit: 1, // Assuming one record per product
            });
            return stock.length ? stock[0].quantity : 0;
        }

        async updatePriceAndStock() {
            const stock = await this.getStock();
            const priceElement = this.el.querySelector('.price-tag');
            const priceText = priceElement.textContent.trim();
            priceElement.textContent = `${priceText} - Stock: ${stock}`;
        }

        mounted() {
            super.mounted();
            this.updatePriceAndStock();
        }
    }

    return CustomProductItem;
});
