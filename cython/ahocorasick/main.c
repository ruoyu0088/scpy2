#include <stdio.h>
#include "ahocorasick.h"

/* 搜索关键字列表 */
AC_ALPHABET_t * allstr[] = {
    "recent", "from", "college"
};

#define PATTERN_NUMBER (sizeof(allstr)/sizeof(AC_ALPHABET_t *))

/* 搜索文本 */
AC_ALPHABET_t * input_text = {"She recently graduated from college"};

//*** 匹配时的回调函数
int match_handler(AC_MATCH_t * m, void * param)
{
    unsigned int j;

    printf ("@ %ld : %s\n", m->position, m->patterns->astring);
    /* 返回0继续搜索，返回1停止搜索 */
    return 0;
}

int main (int argc, char ** argv)
{
    unsigned int i;

    AC_AUTOMATA_t * acap;
    AC_PATTERN_t tmp_patt;
    AC_TEXT_t tmp_text;

    //*** 创建AC_AUTOMATA_t结构体，并传递回调函数
    acap = ac_automata_init();

    //*** 添加关键字
    for (i=0; i<PATTERN_NUMBER; i++)
    {
        tmp_patt.astring = allstr[i];
        tmp_patt.rep.number = i+1; // optional
        tmp_patt.length = strlen(tmp_patt.astring);
        ac_automata_add (acap, &tmp_patt);
    }

    //*** 结束添加关键字
    ac_automata_finalize (acap);

    //*** 设置待搜索字符串
    tmp_text.astring = input_text;
    tmp_text.length = strlen(tmp_text.astring);

    //*** 搜索
    ac_automata_search (acap, &tmp_text, 0, match_handler, NULL);

    //*** 释放内存
    ac_automata_release (acap);
    return 0;
}