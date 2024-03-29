=============================
Point of Sale - Minimize Menu
=============================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:bc36a1da44c6db76a0ff464f58f1511761851ac5673829cda4f6cb9efb53c881
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fpos-lightgray.png?logo=github
    :target: https://github.com/OCA/pos/tree/16.0/pos_minimize_menu
    :alt: OCA/pos
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/pos-16-0/pos-16-0-pos_minimize_menu
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/pos&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module allows you to minimize the placeholder that contains
all the options in main point of sale menu part.

It allows to have more place for the display of the current ticket.

**Without this module:**

  .. image:: https://raw.githubusercontent.com/OCA/pos/16.0/pos_minimize_menu/static/img/without_module.png

**with this module:**

  .. image:: https://raw.githubusercontent.com/OCA/pos/16.0/pos_minimize_menu/static/img/with_module.png

**Table of contents**

.. contents::
   :local:

Configuration
=============

if you want to display in the main screen some important buttons:

* Go to 'Point of Sale > Configuration > Settings'

* Edit the field 'Important Buttons' and write the technical name of the buttons.

  .. image:: https://raw.githubusercontent.com/OCA/pos/16.0/pos_minimize_menu/static/img/configure_important_buttons.png

Here are for the official modules, the following possibles values:

  * ``point_of_sale`` : ProductInfoButton, SetFiscalPositionButton, OrderlineCustomerNoteButton, SetPricelistButton, RefundButton

  * ``pos_sale``: SetSaleOrderButton

  * ``pos_discount``: DiscountButton

  * ``pos_loyalty``: RewardButton, ResetProgramsButton, eWalletButton, PromoCodeButton

  * ``pos_restaurant``: SplitBillButton, SubmitOrderButton, TransferOrderButton, PrintBillButton, TableGuestsButton, OrderlineNoteButton

As a result, selected buttons will be displayed in the main screen:

  .. image:: https://raw.githubusercontent.com/OCA/pos/16.0/pos_minimize_menu/static/img/important_buttons_displayed.png

Development
===========

Technically, it provides the same UI for the desktop version
as for the mobile version.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/pos/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/pos/issues/new?body=module:%20pos_minimize_menu%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* GRAP

Contributors
~~~~~~~~~~~~

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-legalsylvain| image:: https://github.com/legalsylvain.png?size=40px
    :target: https://github.com/legalsylvain
    :alt: legalsylvain

Current `maintainer <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-legalsylvain| 

This module is part of the `OCA/pos <https://github.com/OCA/pos/tree/16.0/pos_minimize_menu>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
