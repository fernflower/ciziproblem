# ciziproblem

## About

Inspired by [РосЯма](https://rosyama.ru/) - the project that made responsible governmental authorities in Russia to actually fix thousands of pothoals by automating
the process of complaints creation.

This project aims at helping foreigners in the Czech Republic to combat the common practice of missing deadlines for various residence permit applications by
the Ministry of Interior offices.
Although the deadlines are set by law [Zákon č. 326/1999 Sb.](https://www.zakonyprolidi.cz/cs/1999-326) - a lot of cases never get the final decision in time.
The only real way to speed up the process is to write a complaint to the special Committee, which is a tricky complicated procedure for the majority of foreigners as
the Ministry of Interior doesn't provide the complaint form, the application is required to be in Czech and contain references to the actual law paragraph
to be applied.

Some kinds of applications - like permanent residence permit application - are essential to the foreigner's family wellbeing (due to the 
unprecedented in the EU practice of letting third-country residents' children to get proper medical coverage through national health insurance system enrollment
[only after they obtain a permanent residence permit](https://pvzpnenivzp.cz)). It would be cruel and ignorant not to try to do something about it.

## Getting started

The deployment is docker-compose-friendly and thus straightforward:

`docker-compose up`

This will start the server at `http://localhost:7777`.

## To be done

- [ ] Deploy at https://ciziproblem.cz
- [ ] Make webui more mature
- [ ] i18n support, russian/english at least
- [x] Add license
- [ ] Add kind reminder for speeding up the process of permanent/long-term residence permit when the deadline has not yet passed
- [ ] Add complaint for long-term residence permit
