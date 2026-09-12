class ProductCollector:

    def __init__(
        self,
        paginator,
        checkpoint,
        target_count=1000
    ):
        self.paginator = paginator
        self.checkpoint = checkpoint
        self.target_count = target_count

    # async def collect(self):

    #     state = self.checkpoint.load()

    #     products = list(
    #         state.get("products", [])
    #     )

    #     seen_urls = set(
    #         state.get("seen_urls", [])
    #     )

    #     last_completed_page = state.get(
    #         "last_completed_page",
    #         0
    #     )

    #     page = last_completed_page + 1

    #     while len(products) < self.target_count:

    #         page_products = (
    #             await self.paginator.fetch_page(page)
    #         )

    #         new_products = []

    #         for product in page_products:

    #             source_url = product.get(
    #                 "source_url"
    #             )

    #             if not source_url:
    #                 continue

    #             if source_url in seen_urls:
    #                 continue

    #             seen_urls.add(source_url)

    #             new_products.append(product)

    #         products.extend(new_products)

    #         self.checkpoint.save(
    #             last_completed_page=page,
    #             products=products
    #         )

    #         print(
    #             f"Page {page}: "
    #             f"{len(page_products)} fetched, "
    #             f"{len(new_products)} new, "
    #             f"total={len(products)}"
    #         )

    #         if len(products) >= self.target_count:
    #             break

    #         page += 1

    #     products = products[
    #         :self.target_count
    #     ]

    #     return products
    async def collect(self):

        state = self.checkpoint.load()

        products = list(
            state.get("products", [])
        )

        seen_urls = set(
            state.get("seen_urls", [])
        )

        last_completed_page = state.get(
            "last_completed_page",
            0
        )

        page = last_completed_page + 1

        while len(products) < self.target_count:

            page_products = (
                await self.paginator.fetch_page(page)
            )

            new_products = []

            for product in page_products:

                source_url = product.get(
                    "source_url"
                )

                if not source_url:
                    continue

                if source_url in seen_urls:
                    continue

                seen_urls.add(source_url)

                new_products.append(product)

        # Stop if this page contains
        # no previously unseen products.
            if not new_products:
                print(
                    f"Page {page}: "
                    f"{len(page_products)} fetched, "
                    f"0 new. "
                    f"Stopping pagination."
                )
                break

            products.extend(new_products)

            self.checkpoint.save(
                last_completed_page=page,
                products=products
            )

            print(
                f"Page {page}: "
                f"{len(page_products)} fetched, "
                f"{len(new_products)} new, "
                f"total={len(products)}"
            )

            if len(products) >= self.target_count:
                break

            page += 1

        products = products[
            :self.target_count
        ]

        return products