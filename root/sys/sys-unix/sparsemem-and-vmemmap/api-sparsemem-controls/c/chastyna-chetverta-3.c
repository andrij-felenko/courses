#include <linux/mm.h>
#include <linux/mmzone.h>
#include <linux/memory_hotplug.h>

static void describe_pfn(unsigned long pfn)
{
        struct mem_section *ms;
        struct page *pg;

        if (!pfn_valid(pfn)) {
                pr_info("pfn %lu: описувача немає\n", pfn);
                return;   /* pfn_to_page() тут поклав би ядро */
        }
        ms = __pfn_to_section(pfn);
        pg = pfn_to_online_page(pfn);         /* NULL, якщо секція не в роботі */

        pr_info("pfn %lu  секція %lu  present=%d early=%d online=%d  page=%px\n",
                pfn, pfn_to_section_nr(pfn),
                !!present_section(ms), !!early_section(ms), !!online_section(ms), pg);
}
