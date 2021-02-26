# ciziproblem

## About

Inspired by [РосЯма](https://rosyama.ru/) – the project that made responsible governmental authorities in Russia to actually fix thousands of potholes by automating the process of complaints creation.

This project aims at helping foreigners in the Czech Republic to overcome the common practice of missing deadlines for various residence permit applications by
the Ministry of Interior offices.
Although the deadlines are set by law [Zákon č. 326/1999 Sb.](https://www.zakonyprolidi.cz/cs/1999-326) – a lot of cases never get the final decision in time.
The only real way to speed up the process is to write a complaint to the special Committee, which is a tricky and complicated procedure for the majority of foreigners as the Ministry of Interior doesn't provide the complaint form, the application is required to be in Czech and contain references to the actual law paragraph to be applied.

Some kinds of applications – like permanent residence permit application – are essential for the foreigner's family wellbeing. For example the
unprecedented in the EU practice of denying third–country residents' children proper health coverage through national health insurance system enrollment
[can be mitigated only by obtaining a permanent residence permit](https://pvzpnenivzp.cz). It would be cruel and ignorant not to do something about it.

## Getting started

The deployment is docker–compose–friendly and thus straightforward:

`docker-compose up`

This will start the server at `http://localhost:7777`.

You can also run the development version with `python bottle_app.py`, this will start a dev webserver at `http://localhost:8080`.

## To be done

- [x] Deploy at https://ciziproblem.cz
- [x] Make webui more mature
- [ ] i18n support, russian/english at least
- [x] Add license
- [x] Add kind reminder for speeding up the process of permanent/long-term residence permit when the deadline has not yet passed
- [x] Add complaint for long-term residence permit
- [ ] Support pdf application templates
