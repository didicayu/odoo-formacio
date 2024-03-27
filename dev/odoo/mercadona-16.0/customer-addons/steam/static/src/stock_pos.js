///** @odoo-module **/
//
//import { Component, useState } from "@odoo/owl";
//
//const ProductItem = require('point_of_sale.ProductItem');
//const PosComponent = require('point_of_sale.PosComponent');
//
//export class StockCount extends ProductItem {
//    setup() {
//        this.stock = 0;
//        debug.log("a")
//    }
//}
//
//StockCount.template = "point_of_sale.ProductItem";

odoo.define("steam.ProductItem", function (require) {
    "use strict";

    const ProductItem = require("point_of_sale.ProductItem");

    const StockCount = (ProductItem) =>
        class StockCount extends ProductItem {
            async onProductInfoClick(event) {
                event.stopPropagation();
                return await super.onProductInfoClick(...arguments);
            }
        };

    Registries.Component.extend(ProductItem, QuickInfoProductItem);

    return QuickInfoProductItem;
});